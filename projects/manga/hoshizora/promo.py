"""Vertical promo (1080x1920, under a minute) for HOSHIZORA, cut from the finished video.

  python3 projects/manga/hoshizora/promo.py

Needs the rendered video (output/manga/hoshizora/hoshizora.mp4), its per-scene audio (scene timings come from it),
the thumbnail art (thumb/art-a.png) and Hana's closing line (promo/end_voice.wav).
It builds up to the chef reveal without showing the ending, then an end card: "Watch the full video on the channel".
Output: output/manga/hoshizora/promo/hoshizora_promo.mp4
"""
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "output" / "manga" / "hoshizora"
PROMO = OUT / "promo"
FONT = "/usr/share/fonts/opentype/inter/Inter-BlackItalic.otf"
W, H = 1080, 1920
FG_Y = 656  # where the 16:9 picture sits (1080x608)

# scenes from the video, in order: the hook, the bullying, the booking, the reunion, the reveal (no ending)
SCENES = [0, 4, 7, 30, 32, 39, 44, 49, 60, 62, 63]
TOP = [("MY BULLY BOOKED", "#FFFFFF", 92), ("MY RESTAURANT...", "#FFD43B", 92)]
BOTTOM = [("HE HAD NO IDEA", "#FFFFFF", 84), ("I WAS THE CHEF", "#FFD43B", 96)]
END_TOP = [("WANT TO SEE", "#FFFFFF", 92), ("WHAT HAPPENS NEXT?", "#FFD43B", 76)]
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


# the picture in the middle, a blurred and darkened copy of it filling the frame, then the words on top
LAYOUT = ("[0:v]split[a][b];[a]scale=-2:{H},crop={W}:{H},boxblur=30:3,eq=brightness=-0.25[bg];"
          "[b]scale={W}:608[fg];[bg][fg]overlay=0:{FG_Y}[v0];[v0][1:v]overlay=0:0,fps=30,format=yuv420p[v]").format(W=W, H=H, FG_Y=FG_Y)


def main():
    spec = json.loads((HERE / "script.json").read_text())
    PROMO.mkdir(parents=True, exist_ok=True)
    pad = spec.get("scene_pad", 0.7)
    durs = [duration(OUT / f"scene{i:02d}.mp3") + pad for i in range(len(spec["scenes"]))]
    starts = [sum(durs[:i]) for i in range(len(durs))]
    overlay(TOP, BOTTOM, PROMO / "words.png")
    overlay(END_TOP, END_BOTTOM, PROMO / "words_end.png", button=True)
    parts = []
    for n, i in enumerate(SCENES):
        a, b = starts[i] + 0.3, starts[i] + durs[i] - 0.35  # stay clear of the crossfades into the next scene
        part = PROMO / f"part{n:02d}.mp4"
        run("ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", str(OUT / "hoshizora.mp4"),
            "-i", str(PROMO / "words.png"), "-filter_complex",
            LAYOUT + f";[0:a]afade=t=in:d=0.06,afade=t=out:st={b - a - 0.08:.3f}:d=0.08,aresample=44100[a]",
            "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-c:a", "aac", "-b:a", "192k",
            "-ac", "2", str(part))
        parts.append(part)
    # end card: the thumbnail art, Hana's line, a short pause after it
    end = PROMO / "part_end.mp4"
    voice = PROMO / "end_voice.wav"
    t = duration(voice) + 1.2
    run("ffmpeg", "-v", "error", "-y", "-loop", "1", "-t", f"{t:.3f}", "-i", str(OUT / "thumb" / "art-a.png"),
        "-i", str(PROMO / "words_end.png"), "-i", str(voice), "-filter_complex",
        LAYOUT.replace("[0:v]split", "[0:v]zoompan=z='1+0.0008*on':d=1:s=1920x1080:fps=30,split")
        + f";[2:a]adelay=300|300,apad,atrim=0:{t:.3f},aresample=44100,volume=1.3[a]",
        "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-c:a", "aac", "-b:a", "192k",
        "-ac", "2", "-t", f"{t:.3f}", str(end))
    parts.append(end)
    listing = PROMO / "parts.txt"
    listing.write_text("".join(f"file '{p.name}'\n" for p in parts))
    final = PROMO / "hoshizora_promo.mp4"
    run("ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(listing), "-c:v", "libx264", "-crf", "18",
        "-preset", "medium", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(final))
    print(f"{final} ({duration(final):.1f}s)")


if __name__ == "__main__":
    main()
