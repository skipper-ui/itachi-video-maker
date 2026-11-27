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
    # profile picture: shown as a small circle, so her face and waving hand are close together in the middle
    "square": (f"close-up of {HANA} smiling happily with both eyes wide open and looking straight at the viewer, "
               "two identical big sparkling violet eyes, symmetrical face, waving hi with one open hand raised right "
               "beside her cheek: a normal hand with all five fingers spread apart (thumb and four fingers), palm "
               "facing the viewer; her face and hand fill the middle of the picture, background of soft pink and "
               "orange bokeh lights with little hearts and sparkles", "768x768"),
    # welcome post
    "post": (f"{HANA} from the chest up, smiling happily with both eyes wide open and looking straight at the viewer, "
             "giving a cute peace sign next to her cheek with one hand: exactly two raised fingers (index and middle "
             "finger in a V), the ring finger, little finger and thumb folded down, a normal five-fingered hand; her "
             "face in the middle of the picture with space above and below, background of soft pink and orange "
             "bokeh lights with little hearts and sparkles", "768x768"),
    "wide": (f"{HANA} on the right side of the picture, waist-up, cheerfully holding an open manga book and giving a "
             "peace sign, the left two-thirds of the picture is an open background of a glowing pink and orange sunset "
             "sky over a cozy anime city with floating manga pages and little sparkles", "1024x576"),
    # the banner's strip: a 4:1 picture for the band desktops show, with Hana's whole head inside the phone area
    "strip": ("wide panoramic banner illustration: slightly right of centre, " + HANA + " shown from the chest up, "
              "smiling happily with both eyes open, giving a cute peace sign next to her cheek with one hand: exactly two "
              "raised fingers (index and middle finger in a V), the ring finger, little finger and thumb folded down, "
              "a normal five-fingered hand; her other hand below the picture; her whole head and cat ears "
              "fully visible in the middle of the picture height with space above them; the left half is a glowing pink "
              "and orange sunset sky over a cozy anime city with floating manga pages and little sparkles; on the far "
              "right, more of the city at sunset", "1792x448"),
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

    # profile picture: Hana's face and waving hand, it is shown as a small circle
    cover(sq, 800, 800, 0.5, 0.5).save(OUT / "profile.png")

    # banner: 2560x1440. Desktops show the band y 510-933 across the full width; phones show only its middle,
    # x 507-2053 (the "All devices" box), so the whole strip, Hana and the name are scaled to fit inside that box.
    # The band's sides get a bigger, softened copy of the strip; TVs also see a blurred copy above and below.
    raw = Image.open(OUT / "art-strip.png").convert("RGB")
    b = cover(raw, 2560, 1440).filter(ImageFilter.GaussianBlur(40))
    b = Image.blend(b, Image.new("RGB", b.size, (40, 10, 40)), 0.25)
    band = cover(raw, 2560, 423).filter(ImageFilter.GaussianBlur(3))
    band = Image.blend(band, Image.new("RGB", band.size, (40, 10, 40)), 0.2)
    b.paste(band, (0, 510))
    h = 423
    w = round(raw.width * h / raw.height)  # 1692: a little wider than the phone box
    card = raw.resize((w, h), Image.LANCZOS)
    fade = Image.new("L", card.size, 255)
    fd = ImageDraw.Draw(fade)
    for i in range(60):  # feather the card's left and right edges into the band
        fd.line((i, 0, i, h), fill=round(255 * i / 60))
        fd.line((w - 1 - i, 0, w - 1 - i, h), fill=round(255 * i / 60))
    x0 = (2560 - w) // 2
    b.paste(card, (x0, 510), fade)
    shade = Image.new("L", b.size, 0)
    ImageDraw.Draw(shade).ellipse((1530, 520, 2080, 925), fill=150)
    b = Image.composite(Image.new("RGB", b.size), b, shade.filter(ImageFilter.GaussianBlur(60)))
    d = ImageDraw.Draw(b)
    cx = 1765  # right of Hana, inside the phone box (x 507-2053, y 510-933)
    words(d, "MANGA", cx, 540, 112, "#FFD43B")
    words(d, "FEVER", cx, 656, 112, "#FFD43B")
    words(d, "MANGA & MANHWA DUBS", cx, 795, 36, "#FFFFFF")
    words(d, "NEW STORIES EVERY DAY", cx, 843, 36, "#FF9EC7")
    b.save(OUT / "banner.png")

    # welcome post: 1080x1080
    p = cover(Image.open(OUT / "art-post.png").convert("RGB"), 1080, 1080, 0.5, 0.5)
    shade = Image.new("L", p.size, 0)
    sd = ImageDraw.Draw(shade)
    sd.rectangle((0, 0, 1080, 230), fill=130)
    sd.rectangle((0, 830, 1080, 1080), fill=120)
    p = Image.composite(Image.new("RGB", p.size), p, shade.filter(ImageFilter.GaussianBlur(50)))
    d = ImageDraw.Draw(p)
    words(d, "WELCOME TO", 540, 40, 72, "#FFFFFF")
    words(d, NAME + "!", 540, 118, 104, "#FFD43B")
    words(d, "MANGA & MANHWA DUBS", 540, 850, 66, "#FFFFFF")
    words(d, "NEW STORIES EVERY DAY", 540, 940, 66, "#FF9EC7")
    p.save(OUT / "welcome_post.png")
    for n in ("profile", "banner", "welcome_post"):
        print(OUT / f"{n}.png")


if __name__ == "__main__":
    if sys.argv[1:] != ["text"]:
        draw()
    layout()
