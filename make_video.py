"""Turn a project script into a narrated, captioned video.

Usage:
    uv run make_video.py projects/<name>/script.json [--images fal|magichour] [--force]

For each scene the pipeline generates narration (ElevenLabs, with word
timings) and a clip: either an AI image (fal.ai FLUX or Magic Hour) turned
into a Ken Burns clip, or, with "visuals": "motion" in the script, a canvas
animation from the project's motion.html rendered by motion/render.js. It then
crossfades the clips, lays the narration underneath and burns in captions.
Generated assets are cached in output/<name>/ so re-runs only redo what
changed; pass --force to regenerate everything.
"""

import argparse
import base64
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

FPS = 30
SCENE_PAD = 0.45  # seconds of silence after each scene's narration
XFADE = 0.5  # crossfade length between scenes
TTS_MODEL = "eleven_multilingual_v2"
IMAGE_MODEL = "fal-ai/flux/dev"
# Magic Hour free accounts are limited to 640px output; paid tiers can raise these.
MH_MODEL = os.environ.get("MAGIC_HOUR_MODEL", "qwen-image-2.1")
MH_RESOLUTION = os.environ.get("MAGIC_HOUR_RESOLUTION", "640px")
TTS_SLOTS = threading.Semaphore(2)  # ElevenLabs plans cap concurrent requests


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def probe_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        check=True, capture_output=True, text=True,
    ).stdout
    return float(out.strip())


def fingerprint(*parts):
    return hashlib.sha256(json.dumps(parts, sort_keys=True).encode()).hexdigest()[:16]


def is_fresh(path, key):
    """True if `path` exists and was built from inputs hashing to `key`."""
    stamp = path.with_suffix(path.suffix + ".key")
    return path.exists() and stamp.exists() and stamp.read_text() == key


def mark(path, key):
    path.with_suffix(path.suffix + ".key").write_text(key)


# --- narration -------------------------------------------------------------

ELEVEN_KEY_VARS = ("ELEVENLABS_API_KEY", "ELEVENLABS_API_KEY_2")
_spent_keys = set()          # key variables that have run out of credit this run
_spent_lock = threading.Lock()


def _out_of_credit(r):
    if r.status_code not in (401, 402):
        return False
    try:
        detail = r.json().get("detail", {})
    except ValueError:
        return False
    return isinstance(detail, dict) and detail.get("code") in ("quota_exceeded", "insufficient_credits")


def eleven_post(url, body, timeout):
    """POST to ElevenLabs with the first key that still has credit, falling back to the next on quota errors."""
    keys = [v for v in ELEVEN_KEY_VARS if os.environ.get(v)]
    last = None
    for var in keys:
        with _spent_lock:
            if var in _spent_keys:
                continue
        for attempt in range(5):
            with TTS_SLOTS:
                r = requests.post(url, headers={"xi-api-key": os.environ[var]}, json=body, timeout=timeout)
            if r.status_code != 429:
                break
            time.sleep(2 ** attempt)
        if _out_of_credit(r):
            with _spent_lock:
                if var not in _spent_keys:
                    _spent_keys.add(var)
                    print(f"  {var} is out of credit, switching to the next key")
            last = r
            continue
        return r
    if last is None:
        raise RuntimeError("No ElevenLabs key with credit left (set ELEVENLABS_API_KEY / ELEVENLABS_API_KEY_2 in .env)")
    return last


def synthesize(scene_idx, scenes, voice_id, out_dir, force):
    text = scenes[scene_idx]["narration"]
    audio = out_dir / f"scene{scene_idx:02d}.mp3"
    timing = out_dir / f"scene{scene_idx:02d}.timing.json"
    key = fingerprint(text, voice_id, TTS_MODEL)
    if not force and is_fresh(audio, key) and timing.exists():
        return
    body = {
        "text": text,
        "model_id": TTS_MODEL,
        "voice_settings": {"stability": 0.45, "similarity_boost": 0.8, "style": 0.35},
    }
    # Neighbouring text keeps intonation consistent across separately generated scenes.
    if scene_idx > 0:
        body["previous_text"] = scenes[scene_idx - 1]["narration"]
    if scene_idx + 1 < len(scenes):
        body["next_text"] = scenes[scene_idx + 1]["narration"]
    r = eleven_post(f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps", body, 120)
    r.raise_for_status()
    data = r.json()
    audio.write_bytes(base64.b64decode(data["audio_base64"]))
    timing.write_text(json.dumps(data["alignment"]))
    mark(audio, key)
    print(f"  narration {scene_idx + 1}/{len(scenes)} done")


def words_from_alignment(alignment):
    """Collapse per-character timings into (word, start, end) tuples."""
    words, current, start, end = [], "", None, None
    for ch, s, e in zip(alignment["characters"],
                        alignment["character_start_times_seconds"],
                        alignment["character_end_times_seconds"]):
        if ch.isspace():
            if current:
                words.append((current, start, end))
            current, start = "", None
            continue
        if start is None:
            start = s
        current += ch
        end = e
    if current:
        words.append((current, start, end))
    return words


# --- images ----------------------------------------------------------------

def generate_image(provider, scene_idx, prompt, width, height, out_dir, force):
    path = out_dir / f"scene{scene_idx:02d}.png"
    model = IMAGE_MODEL if provider == "fal" else (MH_MODEL, MH_RESOLUTION)
    key = fingerprint(prompt, width, height, provider, model)
    if not force and is_fresh(path, key):
        return
    if provider == "magichour":
        magic_hour_image(scene_idx, prompt, width, height, out_dir.name, path)
    else:
        fal_image(scene_idx, prompt, width, height, path)
    mark(path, key)
    print(f"  image {scene_idx + 1} done")


def magic_hour_image(scene_idx, prompt, width, height, project, path):
    from magic_hour import Client

    client = Client(token=os.environ["MAGIC_HOUR_API_KEY"])
    aspect = "9:16" if height > width else "16:9" if width > height else "1:1"
    with tempfile.TemporaryDirectory() as tmp:
        result = client.v1.ai_image_generator.generate(
            image_count=1, aspect_ratio=aspect, model=MH_MODEL, resolution=MH_RESOLUTION,
            style={"prompt": prompt}, name=f"{project}-scene{scene_idx:02d}",
            download_directory=tmp,
        )
        if result.status != "complete" or not result.downloaded_paths:
            raise RuntimeError(f"Magic Hour image {scene_idx + 1} failed: {result.status} {result.error}")
        shutil.move(result.downloaded_paths[0], path)


def fal_image(scene_idx, prompt, width, height, path):
    r = requests.post(
        f"https://fal.run/{IMAGE_MODEL}",
        headers={"Authorization": f"Key {os.environ['FAL_KEY']}"},
        json={
            "prompt": prompt,
            # FLUX wants dimensions divisible by 16; we crop to the exact size later.
            "image_size": {"width": -(-width // 16) * 16, "height": -(-height // 16) * 16},
            "num_inference_steps": 28,
            "guidance_scale": 3.5,
            "seed": 1000 + scene_idx,
            "enable_safety_checker": True,
            "output_format": "png",
        },
        timeout=300,
    )
    r.raise_for_status()
    url = r.json()["images"][0]["url"]
    img = requests.get(url, timeout=120)
    img.raise_for_status()
    path.write_bytes(img.content)


# --- video -----------------------------------------------------------------

# Motion effects layered over each Ken Burns clip. A scene picks them with "fx" in its script.
FX_DEFAULT = ["snow"]


def particles(label, w, h, seconds, cell, density, blur, fall, drift, tint=(1, 1, 1), strength=1.0):
    """A layer of soft dots that scrolls across the frame (snow falling, embers rising).

    A random still texture is drawn once at low resolution, thresholded into sparse dots,
    scaled up and blurred into soft flakes, then scrolled with wrap-around every frame.
    """
    lw, lh = w // cell, h // cell
    # ffmpeg's uniform noise on mid-gray spans roughly 76-175, about 1% of pixels per value.
    cut = 175 - max(1, round(100 * density))
    peak = round(255 * strength)
    r, g, b = tint
    return (
        f"color=c=gray:s={lw}x{lh}:r={FPS}:d={seconds:.3f},format=gray,"
        f"noise=c0s=100:c0f=u,lut=c0='if(gt(val,{cut}),{peak},0)',"
        f"scale={w}:{h}:flags=bicubic,gblur=sigma={blur},"
        f"scroll=v={fall}:h={drift},format=gbrp,"
        f"lutrgb=r='val*{r}':g='val*{g}':b='val*{b}'[{label}]"
    )


def mist(label, w, h, seconds, strength=0.35):
    """Big soft cloud shapes drifting sideways."""
    return (
        f"color=c=gray:s=18x32:r={FPS}:d={seconds:.3f},format=gray,"
        f"noise=c0s=100:c0f=u,lut=c0='max(val-118,0)*{strength * 3.5}',"
        f"scale={w}:{h}:flags=bicubic,gblur=sigma=60,"
        f"scroll=h=0.0009:v=-0.0002,format=gbrp[{label}]"
    )


def ken_burns_clip(scene_idx, image, seconds, width, height, out_dir, force, fx=None):
    fx = FX_DEFAULT if fx is None else fx
    path = out_dir / f"scene{scene_idx:02d}.mp4"
    key = fingerprint(hashlib.sha256(image.read_bytes()).hexdigest(), seconds, width, height, FPS, fx, "fx-v1")
    if not force and is_fresh(path, key):
        return path
    frames = round(seconds * FPS)
    src_w = int(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width", "-of", "csv=p=0",
                                str(image)], check=True, capture_output=True, text=True).stdout.split()[0])
    sharpen = ",unsharp=5:5:0.8" if src_w < width else ""
    zoom = 0.10
    # Alternate between zooming in and out, and drift in a different direction each scene.
    if scene_idx % 2 == 0:
        z = f"1+{zoom}*on/{frames}"
    else:
        z = f"1+{zoom}-{zoom}*on/{frames}"
    drift = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)][scene_idx % 5]
    x = f"(iw-iw/zoom)/2+{drift[0]}*(iw-iw/zoom)/2*(on/{frames}-0.5)"
    y = f"(ih-ih/zoom)/2+{drift[1]}*(ih-ih/zoom)/2*(on/{frames}-0.5)"
    # Upscale 2x before zoompan: it rounds the crop to whole pixels, which jitters at low res.
    graph = [
        f"[0:v]scale={width}:{height}:force_original_aspect_ratio=increase:flags=lanczos,"
        f"crop={width}:{height}{sharpen},scale={width * 2}:{height * 2}:flags=lanczos,"
        f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={width}x{height}:fps={FPS},format=gbrp[base]"
    ]
    layers = []
    w, h = width, height
    if "snow" in fx or "blizzard" in fx:
        fast = 2 if "blizzard" in fx else 1
        graph.append(particles("far", w, h, seconds, 6, 0.01, 1.2, -0.0022 * fast, 0.0006 * fast, strength=0.75))
        graph.append(particles("near", w, h, seconds, 12, 0.01, 3, -0.0045 * fast, 0.0012 * fast))
        layers += ["far", "near"]
    if "embers" in fx:
        graph.append(particles("embers", w, h, seconds, 8, 0.01, 1.6, 0.0035, -0.0006,
                               tint=(1, 0.55, 0.15)))
        layers.append("embers")
    if "mist" in fx:
        graph.append(mist("mist", w, h, seconds))
        layers.append("mist")
    prev = "[base]"
    for i, layer in enumerate(layers):
        graph.append(f"{prev}[{layer}]blend=all_mode=screen[l{i}]")
        prev = f"[l{i}]"
    post = ["format=yuv420p"]
    brightness = []
    if "pulse" in fx:  # slow breathing glow
        brightness.append("0.045*sin(2*PI*t/1.8)")
    if "impact" in fx:  # white flash shortly after the scene starts, fading fast
        brightness.append("0.4*exp(-5*(t-0.5))*gte(t,0.5)")
    if brightness:
        post.append(f"eq=brightness='{'+'.join(brightness)}':eval=frame")
    shake = 0
    if "shake" in fx:
        shake = 7
    if "impact" in fx:
        shake = 18
    if shake:
        # Jitter a slightly smaller crop around the frame; impact shake dies down after the hit.
        amp = f"{shake}*exp(-1.5*max(t-0.5,0))" if "impact" in fx else str(shake)
        m = shake * 2
        post.append(f"crop=w=iw-{m * 2}:h=ih-{m * 2}:x='{m}+{amp}*sin(t*37)':y='{m}+{amp}*sin(t*29+1)',"
                    f"scale={width}:{height}")
    post.append("vignette=angle=PI/6")
    graph.append(f"{prev}{','.join(post)}[out]")
    run(["ffmpeg", "-y", "-i", str(image), "-filter_complex", ";".join(graph), "-map", "[out]",
         "-frames:v", str(frames), "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "18",
         "-pix_fmt", "yuv420p", str(path)])
    mark(path, key)
    print(f"  clip {scene_idx + 1} done ({seconds:.1f}s, fx: {', '.join(fx) or 'none'})")
    return path


def ass_time(t):
    cs = round(t * 100)
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def motion_clip(scene_idx, page, seconds, words, out_dir, force):
    """Render scene `scene_idx` of a canvas page (see motion/lib.js) to an MP4."""
    path = out_dir / f"scene{scene_idx:02d}.mp4"
    words_path = out_dir / f"scene{scene_idx:02d}.words.json"
    words_path.write_text(json.dumps(words))
    root = Path(__file__).parent
    sources = [page, root / "motion" / "lib.js", root / "motion" / "render.js"]
    key = fingerprint([hashlib.sha256(p.read_bytes()).hexdigest() for p in sources], round(seconds, 3), words, FPS)
    if not force and is_fresh(path, key):
        return path
    run(["node", str(root / "motion" / "render.js"), str(page), str(scene_idx), f"{seconds:.3f}", str(FPS),
         str(path), str(words_path)])
    mark(path, key)
    print(f"  motion clip {scene_idx + 1} done ({seconds:.1f}s)")
    return path


def ass_color(hex_rgb, alpha=0):
    """'#RRGGBB' -> ASS '&HAABBGGRR'."""
    r, g, b = hex_rgb[1:3], hex_rgb[3:5], hex_rgb[5:7]
    return f"&H{alpha:02X}{b}{g}{r}".upper()


CAPTION = {
    "font": "Inter Display Black",
    "base": "#FFFFFF",      # words not yet spoken / already spoken
    "active": "#FFC83D",    # the word being spoken right now
    "keyword": "#8FE3FF",   # names and skills listed in the script's "keywords"
    "max_chars": 16,        # keep chunks short so they read at a glance
}


def chunk_words(words, max_chars, max_words=3):
    """Group words into short caption chunks, breaking early at sentence ends."""
    chunks, cur = [], []
    for w in words:
        if cur and (len(" ".join(x[0] for x in cur + [w])) > max_chars or len(cur) >= max_words):
            chunks.append(cur)
            cur = []
        cur.append(w)
        if w[0][-1] in ".?!:":
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    return chunks


def clean_word(word):
    return word.strip(",.;:\"").upper()


def write_captions(scene_words, scene_starts, width, height, path, keywords=(), title=None, style=None):
    # A script can restyle captions with "caption": {"font", "base", "active", "keyword", "max_chars"}.
    cap = {**CAPTION, **(style or {})}
    keys = {k.upper() for k in keywords}
    size = round(height * 0.058)
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{cap["font"]},{size},{ass_color(cap["base"])},&H000000FF,&H00000000,&H64000000,0,0,0,0,100,100,1,0,1,{round(size * 0.11)},{round(size * 0.07)},2,70,70,{round(height * 0.27)},1
Style: Title,{cap["font"]},{round(height * 0.085)},{ass_color(cap["base"])},&H000000FF,&H00000000,&H64000000,0,0,0,0,100,100,6,0,1,{round(height * 0.006)},{round(height * 0.004)},8,60,60,{round(height * 0.11)},1
Style: Sub,{cap["font"]},{round(height * 0.03)},{ass_color(cap["active"])},&H000000FF,&H00000000,&H64000000,0,0,0,0,100,100,8,0,1,{round(height * 0.0035)},{round(height * 0.003)},8,60,60,{round(height * 0.205)},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    if title:
        main, _, sub = title.partition(":")
        fade = r"{\fad(250,400)\blur0.6}"
        pop = r"{\fad(250,400)\blur0.6\fscx130\fscy130\t(0,350,\fscx100\fscy100)}"
        lines.append(f"Dialogue: 1,{ass_time(0.15)},{ass_time(3.4)},Title,,0,0,0,,{pop}{main.strip().upper()}")
        if sub.strip():
            lines.append(f"Dialogue: 1,{ass_time(0.45)},{ass_time(3.4)},Sub,,0,0,0,,{fade}{sub.strip().upper()}")

    def colored(chunk, active_idx):
        parts = []
        for j, (w, _, _) in enumerate(chunk):
            word = clean_word(w)
            if j == active_idx:
                color = cap["active"]
            elif word.strip("'!?") in keys:
                color = cap["keyword"]
            else:
                color = cap["base"]
            parts.append(f"{{\\1c{ass_color(color)}}}{word}")
        return " ".join(parts)

    for words, offset in zip(scene_words, scene_starts):
        chunks = chunk_words(words, cap["max_chars"])
        for c, chunk in enumerate(chunks):
            # Hold the chunk until the next one starts so captions never blink off mid-sentence.
            chunk_end = chunks[c + 1][0][1] if c + 1 < len(chunks) else chunk[-1][2] + 0.35
            for j, (_, w_start, _) in enumerate(chunk):
                start = offset + w_start
                end = offset + (chunk[j + 1][1] if j + 1 < len(chunk) else chunk_end)
                # The whole chunk pops in on its first word; later words only change colour.
                fx = r"{\blur0.8\fscx82\fscy82\t(0,90,\fscx106\fscy106)\t(90,170,\fscx100\fscy100)}" if j == 0 \
                    else r"{\blur0.8}"
                lines.append(f"Dialogue: 0,{ass_time(start)},{ass_time(end)},Cap,,0,0,0,,{fx}{colored(chunk, j)}")
    path.write_text(header + "\n".join(lines) + "\n")


# --- sound effects & music ---------------------------------------------------

SFX_LIBRARY = Path(__file__).parent / "sfx_library.json"
SFX_DIR = Path(__file__).parent / "assets" / "sfx"


def ensure_sound(name):
    """Return the path of a library sound, generating it with ElevenLabs on first use."""
    spec = json.loads(SFX_LIBRARY.read_text())[name]
    path = SFX_DIR / f"{name}.mp3"
    key = fingerprint(spec)
    if is_fresh(path, key):
        return path
    SFX_DIR.mkdir(parents=True, exist_ok=True)
    body = {"text": spec["prompt"], "duration_seconds": spec["duration"], "prompt_influence": 0.5}
    if spec.get("loop"):
        body["loop"] = True
    r = eleven_post("https://api.elevenlabs.io/v1/sound-generation", body, 180)
    r.raise_for_status()
    path.write_bytes(r.content)
    mark(path, key)
    print(f"  sound '{name}' generated")
    return path


def norm_word(w):
    return "".join(ch for ch in w.lower() if ch.isalnum())


def word_time(words, word, nth=0):
    hits = [w for w in words if norm_word(w[0]) == norm_word(word)]
    if len(hits) <= nth:
        raise ValueError(f"cue word '{word}' not found in narration: {' '.join(w[0] for w in words)}")
    return hits[nth][1]


def sound_cues(scenes, scene_words, starts):
    """Expand each scene's "sfx" list into absolute (time, sound, volume) cues.

    A cue is {"sound": name, "word": w | "at": seconds, "offset": s, "volume": v}, optionally with
    "repeat": n and either "every": s or "until_word": w (+ "until_offset") to spread n hits evenly.
    """
    cues = []
    for scene, words, start in zip(scenes, scene_words, starts):
        for cue in scene.get("sfx", []):
            t0 = (word_time(words, cue["word"], cue.get("nth", 0)) if "word" in cue else cue.get("at", 0.0))
            t0 += cue.get("offset", 0.0)
            n = cue.get("repeat", 1)
            if "until_word" in cue and n > 1:
                t1 = word_time(words, cue["until_word"]) + cue.get("until_offset", 0.0)
                every = (t1 - t0) / (n - 1)
            else:
                every = cue.get("every", 0.0)
            for k in range(n):
                cues.append((max(0.0, start + t0 + k * every), cue["sound"], cue.get("volume", 0.8)))
    return cues


def assemble(clips, audios, durations, captions, out_path, cues=(), music=None):
    n = len(clips)
    total = sum(durations)
    cmd = ["ffmpeg", "-y"]
    for c in clips:
        cmd += ["-i", str(c)]
    for a in audios:
        cmd += ["-i", str(a)]
    sounds = sorted({name for _, name, _ in cues})
    sound_idx = {}
    for name in sounds:
        sound_idx[name] = 2 * n + len(sound_idx)
        cmd += ["-i", str(ensure_sound(name))]
    music_idx = None
    if music:
        music_idx = 2 * n + len(sounds)
        cmd += ["-stream_loop", "-1", "-i", str(ensure_sound(music["sound"]))]
    filters = []
    # Video: chain crossfades; transition k starts when scene k's slot ends.
    prev, offset = "[0:v]", 0.0
    for k in range(1, n):
        offset += durations[k - 1]
        out = f"[v{k}]"
        filters.append(f"{prev}[{k}:v]xfade=transition=fade:duration={XFADE}:offset={offset:.3f}{out}")
        prev = out
    filters.append(f"{prev}ass={captions}[vout]")
    # Narration: pad each scene's voice to its slot, then concatenate.
    for k in range(n):
        filters.append(f"[{n + k}:a]aresample=44100,apad,atrim=0:{durations[k]:.3f}[a{k}]")
    filters.append("".join(f"[a{k}]" for k in range(n)) + f"concat=n={n}:v=0:a=1[narr]")
    mix = ["[voice]"]
    if music_idx is not None:
        # Music ducks under the voice (sidechain) and fades in/out.
        filters.append("[narr]asplit=2[voice][key]")
        filters.append(f"[{music_idx}:a]aresample=44100,atrim=0:{total:.3f},volume={music.get('volume', 0.22)},"
                       f"afade=t=in:d=1,afade=t=out:st={max(0, total - 2):.3f}:d=2[bed]")
        filters.append("[bed][key]sidechaincompress=threshold=0.03:ratio=8:attack=15:release=350[music]")
        mix.append("[music]")
    else:
        filters.append("[narr]anull[voice]")
    # Sound effects: one delayed copy per cue.
    uses = {name: [c for c in cues if c[1] == name] for name in sounds}
    for name, hits in uses.items():
        idx = sound_idx[name]
        labels = [f"[{name}{j}]" for j in range(len(hits))]
        filters.append(f"[{idx}:a]aresample=44100,asplit={len(hits)}" + "".join(labels) if len(hits) > 1
                       else f"[{idx}:a]aresample=44100{labels[0]}")
        for j, (t, _, vol) in enumerate(hits):
            ms = round(t * 1000)
            filters.append(f"{labels[j]}volume={vol},adelay={ms}|{ms}[fx_{name}{j}]")
            mix.append(f"[fx_{name}{j}]")
    filters.append("".join(mix) + f"amix=inputs={len(mix)}:normalize=0:duration=first,"
                   "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=44100[aout]")
    cmd += ["-filter_complex", ";".join(filters), "-map", "[vout]", "-map", "[aout]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{total:.3f}", str(out_path)]
    run(cmd)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("script", type=Path)
    parser.add_argument("--images", choices=["fal", "magichour"],
                        default=os.environ.get("IMAGE_PROVIDER", "fal"),
                        help="image generator (default: $IMAGE_PROVIDER or fal)")
    parser.add_argument("--force", action="store_true", help="regenerate all assets")
    args = parser.parse_args()

    spec = json.loads(args.script.read_text())
    name = args.script.parent.name
    out_dir = Path(__file__).parent / "output" / name
    out_dir.mkdir(parents=True, exist_ok=True)
    width, height = spec["width"], spec["height"]
    scenes = spec["scenes"]
    motion = spec.get("visuals") == "motion"
    prompts = [] if motion else [f"{s['image'].format(character=spec['character'])}, {spec['style']}" for s in scenes]

    print(f"Generating narration{"" if motion else " and images"} for {len(scenes)} scenes...")
    with ThreadPoolExecutor(max_workers=4) as pool:
        jobs = [pool.submit(synthesize, i, scenes, spec["voice_id"], out_dir, args.force) for i in range(len(scenes))]
        if not motion:
            jobs += [pool.submit(generate_image, args.images, i, p, width, height, out_dir, args.force)
                     for i, p in enumerate(prompts)]
        for j in jobs:
            j.result()

    audios = [out_dir / f"scene{i:02d}.mp3" for i in range(len(scenes))]
    durations = [probe_duration(a) + SCENE_PAD for a in audios]
    scene_words = [words_from_alignment(json.loads((out_dir / f"scene{i:02d}.timing.json").read_text()))
                   for i in range(len(scenes))]
    starts = [sum(durations[:i]) for i in range(len(scenes))]

    print("Rendering clips...")
    lengths = [durations[i] + (XFADE if i < len(scenes) - 1 else 0) for i in range(len(scenes))]
    if motion:
        page = args.script.parent / spec.get("motion_page", "motion.html")
        with ThreadPoolExecutor(max_workers=3) as pool:
            clips = list(pool.map(lambda i: motion_clip(i, page, lengths[i], scene_words[i], out_dir, args.force),
                                  range(len(scenes))))
    else:
        # Every clip but the last runs XFADE longer so it can overlap the next scene.
        with ThreadPoolExecutor(max_workers=2) as pool:
            clips = list(pool.map(
                lambda i: ken_burns_clip(i, out_dir / f"scene{i:02d}.png", lengths[i],
                                         width, height, out_dir, args.force, scenes[i].get("fx")),
                range(len(scenes))))

    captions = out_dir / "captions.ass"
    write_captions(scene_words, starts, width, height, captions,
                   keywords=spec.get("keywords", []),
                   title=spec.get("title") if spec.get("title_card", True) else None,
                   style=spec.get("caption"))
    final = out_dir / f"{name}.mp4"
    print("Assembling final video...")
    cues = sound_cues(scenes, scene_words, starts)
    assemble(clips, audios, durations, captions, final, cues=cues, music=spec.get("music"))
    print(f"Done: {final} ({probe_duration(final):.1f}s)")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        sys.exit(f"ffmpeg failed:\n{e.stderr.decode()[-2000:]}")
    except requests.HTTPError as e:
        sys.exit(f"API error {e.response.status_code}: {e.response.text[:500]}")
