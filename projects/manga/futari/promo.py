"""Vertical promo (1080x1920, about a minute) for FUTARI, cut from the finished video.

  python3 projects/manga/futari/promo.py

Needs the rendered video (output/manga/futari/futari.mp4), its per-scene audio (scene timings come from it) and the
thumbnail's twins art (thumb/art-r.png). Hana's closing line (promo/end_voice.wav) is voiced with ElevenLabs if missing.
It builds up to "there were two of them" without showing the ending, then an end card: "Watch the full video on the channel".
Subtitle colours follow the channel style: pink for female speakers, blue for male ones, yellow italics for narration.
Output: output/manga/futari/promo/futari_promo.mp4
"""
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "output" / "manga" / "futari"
PROMO = OUT / "promo"
FONT = "/usr/share/fonts/opentype/inter/Inter-BlackItalic.otf"
FONTS = "/usr/share/fonts/opentype/inter"
W, H = 1080, 1920
OFFSET = 0.0  # scene audio starts at the scene start
FG_Y = 656  # where the 16:9 picture sits (1080x608)

# scenes from the video, in order: the lie, the mall, leaving Tokyo, the bus, "I'm not Hikari", two of them (no ending)
SCENES = [2, 4, 12, 36, 37, 39, 41, 42, 43]
TOP = [("MY GIRLFRIEND", "#FFFFFF", 92), ("LIED TO ME...", "#FF5CC8", 92)]
END_LINE = "Want to know who Ren chooses? Watch the full video on the channel!"
HOST_VOICE = "vGQNBgLaiM3EdZtxIiuY"  # Aerisita, Hana's voice
MALE, FEMALE = {"ren", "kaito", "daisuke"}, {"hikari", "akari", "grandma", "host"}
END_TOP = [("WHO WILL", "#FFFFFF", 92), ("HE CHOOSE?", "#FF5CC8", 104)]
END_BOTTOM = [("WATCH THE FULL VIDEO", "#FFFFFF", 80), ("ON THE CHANNEL!", "#FFD43B", 104)]


def run(*cmd):
    subprocess.run(cmd, check=True)


def duration(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                                capture_output=True, text=True, check=True).stdout)


def overlay(top, bottom, path, button=False):
    """Transparent 1080x1920 PNG with the words above and below the picture."""
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    def block(lines, y):
        for words, colour, size in lines:
            f = ImageFont.truetype(FONT, size)
            x = (W - d.textlength(words, font=f)) / 2
            d.text((x + 5, y + 7), words, font=f, fill="#000000", stroke_width=11, stroke_fill="#000000")
            d.text((x, y), words, font=f, fill=colour, stroke_width=9, stroke_fill="#000000")
            y += size * 1.12
        return y

    block(top, FG_Y - 60 - sum(s * 1.12 for *_, s in top))
    y = block(bottom, FG_Y + 608 + 60)
    if button:  # a red "subscribe"-style button under the words
        f = ImageFont.truetype(FONT, 54)
        label = "TAP THE CHANNEL NAME"
        tw = d.textlength(label, font=f)
        bx, by = (W - tw) / 2 - 36, y + 40
        d.rounded_rectangle((bx, by, bx + tw + 72, by + 96), 22, fill="#E62117", outline="#000000", width=5)
        d.text((bx + 36, by + 14), label, font=f, fill="#FFFFFF")
    f = ImageFont.truetype(FONT, 40)
    tag = "MANGA DUB"
    tw = d.textlength(tag, font=f)
    d.rounded_rectangle((W - tw - 72, 70, W - 40, 130), 10, fill="#E62117", outline="#000000", width=4)
    d.text((W - tw - 56, 76), tag, font=f, fill="#FFFFFF")
    img.save(path)


def subtitles(scene, a, length, path):
    """Big subtitles for one clip, under the picture: each spoken line while it is spoken (Shorts are often muted)."""
    import textwrap
    lines = json.loads((OUT / f"scene{scene:02d}.lines.json").read_text())
    t = lambda x: "%d:%02d:%05.2f" % (x // 3600, x % 3600 // 60, x % 60)
    ev = []
    for j, (who, text, s0, _) in enumerate(lines):
        s1 = lines[j + 1][2] if j + 1 < len(lines) else length + a
        s0, s1 = max(0.0, s0 - (a - OFFSET)), min(length, s1 - (a - OFFSET))
        if s1 <= s0:
            continue
        body = "\\N".join(textwrap.wrap(text.upper(), 22))
        style = "Narr" if who == "narrator" else "Boy" if who in MALE else "Girl" if who in FEMALE else "Talk"
        ev.append(f"Dialogue: 0,{t(s0)},{t(s1)},{style},,0,0,0,,{{\\fad(80,60)}}{body}")
    path.write_text(f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Talk,Inter Black,68,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,7,4,8,40,40,{FG_Y + 608 + 70},1
Style: Boy,Inter Black,68,&H00FFB070,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,7,4,8,40,40,{FG_Y + 608 + 70},1
Style: Girl,Inter Black,68,&H00C85CFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,7,4,8,40,40,{FG_Y + 608 + 70},1
Style: Narr,Inter Black,68,&H003BD4FF,&H000000FF,&H00000000,&H80000000,-1,1,0,0,100,100,0,0,1,7,4,8,40,40,{FG_Y + 608 + 70},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(ev) + "\n")


# the picture in the middle, a blurred and darkened copy of it filling the frame, then the words on top
LAYOUT = ("[0:v]split[a][b];[a]scale=-2:{H},crop={W}:{H},boxblur=30:3,eq=brightness=-0.42[bg];"
          "[b]scale={W}:608[fg];[bg][fg]overlay=0:{FG_Y}[v0];[v0][1:v]overlay=0:0,fps=30,format=yuv420p[v]").format(W=W, H=H, FG_Y=FG_Y)


def end_voice(path):
    """Hana's closing line, acted with ElevenLabs v3 in the video tool's environment."""
    code = ("import sys, soundfile as sf; sys.path.insert(0, '.'); import make_video as mv; "
            f"a, sr = mv.eleven_v3_line({'[cheerful] ' + END_LINE!r}, {HOST_VOICE!r}); sf.write({str(path)!r}, a, sr)")
    run("uv", "run", "--extra", "local-audio", "python", "-c", code)


def main():
    spec = json.loads((HERE / "script.json").read_text())
    PROMO.mkdir(parents=True, exist_ok=True)
    pad = spec.get("scene_pad", 0.7)
    durs = [duration(OUT / f"scene{i:02d}.mp3") + pad for i in range(len(spec["scenes"]))]
    starts = [sum(durs[:i]) for i in range(len(durs))]
    overlay(TOP, [], PROMO / "words.png")
    overlay(END_TOP, END_BOTTOM, PROMO / "words_end.png", button=True)
    parts = []
    for n, i in enumerate(SCENES):
        a, b = starts[i] + 0.3, starts[i] + durs[i] - 0.35  # stay clear of the crossfades into the next scene
        part = PROMO / f"part{n:02d}.mp4"
        subs = PROMO / f"part{n:02d}.ass"
        subtitles(i, a - starts[i], b - a, subs)
        run("ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", str(OUT / "futari.mp4"),
            "-i", str(PROMO / "words.png"), "-filter_complex",
            LAYOUT.replace("format=yuv420p[v]", f"subtitles={subs}:fontsdir={FONTS},format=yuv420p[v]")
            + f";[0:a]afade=t=in:d=0.06,afade=t=out:st={b - a - 0.08:.3f}:d=0.08,aresample=44100[a]",
            "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-c:a", "aac", "-b:a", "192k",
            "-ac", "2", str(part))
        parts.append(part)
    # end card: the twins from the thumbnail (a 16:9 slice of the tall panel), Hana's line, a short pause after it
    end = PROMO / "part_end.mp4"
    voice = PROMO / "end_voice.wav"
    if not voice.exists():
        end_voice(voice)
    t = duration(voice) + 1.2
    run("ffmpeg", "-v", "error", "-y", "-loop", "1", "-t", f"{t:.3f}", "-i", str(OUT / "thumb" / "art-r.png"),
        "-i", str(PROMO / "words_end.png"), "-i", str(voice), "-filter_complex",
        LAYOUT.replace("[0:v]split", "[0:v]crop=iw:iw*9/16:0:ih*0.06,zoompan=z='1+0.0008*on':d=1:s=1920x1080:fps=30,split")
        + f";[2:a]adelay=300|300,apad,atrim=0:{t:.3f},aresample=44100,volume=1.3[a]",
        "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-c:a", "aac", "-b:a", "192k",
        "-ac", "2", "-t", f"{t:.3f}", str(end))
    parts.append(end)
    listing = PROMO / "parts.txt"
    listing.write_text("".join(f"file '{p.name}'\n" for p in parts))
    final = PROMO / "futari_promo.mp4"
    run("ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(listing), "-c:v", "libx264", "-crf", "18",
        "-preset", "medium", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(final))
    print(f"{final} ({duration(final):.1f}s)")


if __name__ == "__main__":
    main()
