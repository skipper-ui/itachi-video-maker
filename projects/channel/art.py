"""Manga Fever channel art: profile picture, banner, and a welcome community post, all with Hana (the channel host).

  python3 projects/channel/art.py          # draw the art (local FLUX.2 klein + Real-ESRGAN), then lay out the images
  python3 projects/channel/art.py text     # only redo the layout and words over the art already drawn

Hana is drawn from the same portrait used in the videos' outros, so she looks the same everywhere.
Output: output/channel/profile.png (800x800), banner.png (2560x1440), welcome_post.png (1080x1080)
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "output" / "channel"
PY = Path.home() / ".venvs" / "imagegen" / "bin" / "python"
ESRGAN = Path.home() / "models" / "RealESRGAN_x4plus_anime_6B.pth"
FONT = "/usr/share/fonts/opentype/inter/Inter-BlackItalic.otf"
NAME = "MANGA FEVER"

HANA = ("Hana (a cute cheerful anime girl, a young woman with long pastel pink hair in twin tails tied with red ribbons, "
        "big sparkling violet eyes and rosy cheeks, wearing a pastel pink hoodie with little cat ears on the hood)")
STYLE = ("modern Japanese anime illustration, clean thin black line art, cel shading, bright vivid colors, 2D anime, "
         "no text, no letters, no speech bubbles, no watermark")
# (prompt, size) for each piece of art
ART = {
    "square": (f"close-up of {HANA} smiling happily and waving at the viewer with one hand, winking, face in the centre "
               "of the picture, background of soft pink and orange bokeh lights with little hearts and sparkles", "768x768"),
    "wide": (f"{HANA} on the right side of the picture, waist-up, cheerfully holding an open manga book and giving a "
             "peace sign, the left two-thirds of the picture is an open background of a glowing pink and orange sunset "
             "sky over a cozy anime city with floating manga pages and little sparkles", "1024x576"),
}


def draw():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "refs").mkdir(exist_ok=True)
    if not (OUT / "refs" / "host.png").exists():
        shutil.copy(ROOT / "output" / "manga" / "hoshizora" / "refs" / "host.png", OUT / "refs" / "host.png")
    for k, (prompt, size) in ART.items():
        art = OUT / f"art-{k}.png"
        if art.exists():
            continue
        work = OUT / k
        work.mkdir(exist_ok=True)
        if not (work / "refs").exists():
            shutil.copytree(OUT / "refs", work / "refs")
        script = work / "script.json"
        script.write_text(json.dumps({"style": STYLE, "characters": {"host": HANA},
                                      "scenes": [{"image": prompt, "refs": ["host"]}]}, indent=1))
        subprocess.run([str(PY), str(ROOT / "tools" / "flux_local.py"), str(script), str(work), "--size", size,
                        "--seed", os.environ.get("SEED", "7100")], check=True, cwd=ROOT)
        shutil.copy(work / "scene00.png", art)
        subprocess.run([str(PY), str(ROOT / "tools" / "upscale.py"), str(ESRGAN), str(art)], check=True, cwd=ROOT)


def words(d, text, cx, y, size, colour, stroke=None):
    from PIL import ImageFont
    f = ImageFont.truetype(FONT, size)
    s = stroke or max(4, size // 9)
    x = cx - d.textlength(text, font=f) / 2
    d.text((x + s * 0.6, y + s * 0.8), text, font=f, fill="#000000", stroke_width=s + 2, stroke_fill="#000000")
    d.text((x, y), text, font=f, fill=colour, stroke_width=s, stroke_fill="#000000")


def cover(img, w, h, fx=0.5, fy=0.5):
    """Scale to fill w x h and crop, keeping the point (fx, fy) of the picture in view."""
    from PIL import Image
    k = max(w / img.width, h / img.height)
    img = img.resize((round(img.width * k), round(img.height * k)), Image.LANCZOS)
    x = min(max(0, round(img.width * fx - w / 2)), img.width - w)
    y = min(max(0, round(img.height * fy - h / 2)), img.height - h)
    return img.crop((x, y, x + w, y + h))


def layout():
    from PIL import Image, ImageDraw, ImageFilter
    sq = Image.open(OUT / "art-square.png").convert("RGB")
    wide = Image.open(OUT / "art-wide.png").convert("RGB")

    # profile picture: just Hana's face, it is shown as a small circle
    cover(sq, 800, 800, 0.5, 0.42).save(OUT / "profile.png")

    # banner: 2560x1440; every device shows the middle 1546x423, so the name and Hana's face sit there
    b = cover(wide, 2560, 1440, 0.5, 0.42)
    shade = Image.new("L", b.size, 0)
    ImageDraw.Draw(shade).ellipse((420, 440, 1700, 960), fill=150)
    b = Image.composite(Image.new("RGB", b.size), b, shade.filter(ImageFilter.GaussianBlur(90)))
    d = ImageDraw.Draw(b)
    cx = 1060  # the safe area runs from x 507 to 2053; Hana's face is at its right edge
    words(d, NAME, cx, 548, 136, "#FFD43B")
    words(d, "MANGA & MANHWA DUBS", cx, 722, 52, "#FFFFFF")
    words(d, "NEW STORIES EVERY WEEK", cx, 792, 52, "#FF9EC7")
    b.save(OUT / "banner.png")

    # welcome post: 1080x1080
    p = cover(sq, 1080, 1080, 0.5, 0.5)
    shade = Image.new("L", p.size, 0)
    sd = ImageDraw.Draw(shade)
    sd.rectangle((0, 0, 1080, 230), fill=130)
    sd.rectangle((0, 830, 1080, 1080), fill=120)
    p = Image.composite(Image.new("RGB", p.size), p, shade.filter(ImageFilter.GaussianBlur(50)))
    d = ImageDraw.Draw(p)
    words(d, "WELCOME TO", 540, 40, 72, "#FFFFFF")
    words(d, NAME + "!", 540, 118, 104, "#FFD43B")
    words(d, "MANGA & MANHWA DUBS", 540, 850, 66, "#FFFFFF")
    words(d, "NEW STORIES EVERY WEEK", 540, 940, 66, "#FF9EC7")
    p.save(OUT / "welcome_post.png")
    for n in ("profile", "banner", "welcome_post"):
        print(OUT / f"{n}.png")


if __name__ == "__main__":
    if sys.argv[1:] != ["text"]:
        draw()
    layout()
