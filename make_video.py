"""Turn a project script into a narrated, captioned video.

Usage:
    uv run make_video.py projects/<name>/script.json [--force]

For each scene the pipeline generates narration (ElevenLabs, with word
timings), an image (fal.ai FLUX), and a Ken Burns clip (ffmpeg). It then
crossfades the clips, lays the narration underneath and burns in captions.
Generated assets are cached in output/<name>/ so re-runs only redo what
changed; pass --force to regenerate everything.
"""

import argparse
import base64
import hashlib
import json
import os
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests
from dotenv import load_dotenv

FPS = 30
SCENE_PAD = 0.45  # seconds of silence after each scene's narration
XFADE = 0.5  # crossfade length between scenes
TTS_MODEL = "eleven_multilingual_v2"
IMAGE_MODEL = "fal-ai/flux/dev"
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
    for attempt in range(5):
        with TTS_SLOTS:
            r = requests.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps",
                headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"]},
                json=body, timeout=120,
            )
        if r.status_code != 429:
            break
        time.sleep(2 ** attempt)
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

def generate_image(scene_idx, prompt, width, height, out_dir, force):
    path = out_dir / f"scene{scene_idx:02d}.png"
    key = fingerprint(prompt, width, height, IMAGE_MODEL)
    if not force and is_fresh(path, key):
        return
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
    mark(path, key)
    print(f"  image {scene_idx + 1} done")


# --- video -----------------------------------------------------------------

def ken_burns_clip(scene_idx, image, seconds, width, height, out_dir, force):
    path = out_dir / f"scene{scene_idx:02d}.mp4"
    key = fingerprint(hashlib.sha256(image.read_bytes()).hexdigest(), seconds, width, height, FPS)
    if not force and is_fresh(path, key):
        return path
    frames = round(seconds * FPS)
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
    vf = (
        f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},"
        f"scale={width * 2}:{height * 2}:flags=lanczos,"
        f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={width}x{height}:fps={FPS},"
        f"format=yuv420p"
    )
    run(["ffmpeg", "-y", "-i", str(image), "-vf", vf, "-frames:v", str(frames),
         "-c:v", "libx264", "-preset", "medium", "-crf", "18", str(path)])
    mark(path, key)
    print(f"  clip {scene_idx + 1} done ({seconds:.1f}s)")
    return path


def ass_time(t):
    cs = round(t * 100)
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def write_captions(scene_words, scene_starts, width, height, path, words_per_line=3):
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter ExtraBold,{round(height * 0.042)},&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,{round(height * 0.0045)},{round(height * 0.002)},2,60,60,{round(height * 0.24)},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    for words, offset in zip(scene_words, scene_starts):
        for i in range(0, len(words), words_per_line):
            chunk = words[i:i + words_per_line]
            start = offset + chunk[0][1]
            # Hold each chunk until the next one starts so captions don't flicker.
            nxt = words[i + words_per_line][1] if i + words_per_line < len(words) else chunk[-1][2] + 0.3
            end = offset + nxt
            text = " ".join(w for w, _, _ in chunk).upper()
            lines.append(f"Dialogue: 0,{ass_time(start)},{ass_time(end)},Cap,,0,0,0,,{text}")
    path.write_text(header + "\n".join(lines) + "\n")


def assemble(clips, audios, durations, captions, out_path):
    n = len(clips)
    cmd = ["ffmpeg", "-y"]
    for c in clips:
        cmd += ["-i", str(c)]
    for a in audios:
        cmd += ["-i", str(a)]
    filters = []
    # Video: chain crossfades; transition k starts when scene k's slot ends.
    prev, offset = "[0:v]", 0.0
    for k in range(1, n):
        offset += durations[k - 1]
        out = f"[v{k}]"
        filters.append(f"{prev}[{k}:v]xfade=transition=fade:duration={XFADE}:offset={offset:.3f}{out}")
        prev = out
    filters.append(f"{prev}ass={captions}[vout]")
    # Audio: pad each narration to its scene slot, then concatenate.
    for k in range(n):
        filters.append(f"[{n + k}:a]aresample=44100,apad,atrim=0:{durations[k]:.3f}[a{k}]")
    filters.append("".join(f"[a{k}]" for k in range(n)) + f"concat=n={n}:v=0:a=1[aout]")
    cmd += ["-filter_complex", ";".join(filters), "-map", "[vout]", "-map", "[aout]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out_path)]
    run(cmd)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("script", type=Path)
    parser.add_argument("--force", action="store_true", help="regenerate all assets")
    args = parser.parse_args()

    load_dotenv(Path(__file__).parent / ".env")
    spec = json.loads(args.script.read_text())
    name = args.script.parent.name
    out_dir = Path(__file__).parent / "output" / name
    out_dir.mkdir(parents=True, exist_ok=True)
    width, height = spec["width"], spec["height"]
    scenes = spec["scenes"]
    prompts = [f"{s['image'].format(character=spec['character'])}, {spec['style']}" for s in scenes]

    print(f"Generating narration and images for {len(scenes)} scenes...")
    with ThreadPoolExecutor(max_workers=4) as pool:
        jobs = [pool.submit(synthesize, i, scenes, spec["voice_id"], out_dir, args.force) for i in range(len(scenes))]
        jobs += [pool.submit(generate_image, i, p, width, height, out_dir, args.force) for i, p in enumerate(prompts)]
        for j in jobs:
            j.result()

    audios = [out_dir / f"scene{i:02d}.mp3" for i in range(len(scenes))]
    durations = [probe_duration(a) + SCENE_PAD for a in audios]
    scene_words = [words_from_alignment(json.loads((out_dir / f"scene{i:02d}.timing.json").read_text()))
                   for i in range(len(scenes))]
    starts = [sum(durations[:i]) for i in range(len(scenes))]

    print("Rendering clips...")
    with ThreadPoolExecutor(max_workers=2) as pool:
        # Every clip but the last runs XFADE longer so it can overlap the next scene.
        clips = list(pool.map(
            lambda i: ken_burns_clip(i, out_dir / f"scene{i:02d}.png",
                                     durations[i] + (XFADE if i < len(scenes) - 1 else 0),
                                     width, height, out_dir, args.force),
            range(len(scenes))))

    captions = out_dir / "captions.ass"
    write_captions(scene_words, starts, width, height, captions)
    final = out_dir / f"{name}.mp4"
    print("Assembling final video...")
    assemble(clips, audios, durations, captions, final)
    print(f"Done: {final} ({probe_duration(final):.1f}s)")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        sys.exit(f"ffmpeg failed:\n{e.stderr.decode()[-2000:]}")
    except requests.HTTPError as e:
        sys.exit(f"API error {e.response.status_code}: {e.response.text[:500]}")
