"""Comic-page YouTube thumbnails in the channel's house style (see projects/manga/STYLE.md).

A 1280x720 page on a dark frame: two stacked panels on the left, one tall panel on the right. On top go oval speech
bubbles with no tail (blue words for male speakers, pink for female ones), red-on-white label boxes, a round "chibi"
face inset and the host's portrait in the bottom-left corner.

Use it from a video's thumbnail script:

    from comic_thumb import page
    page({"tl": "art-tl.png", "bl": "art-bl.png", "r": "art-r.png"},
         bubbles=[("r", "WE BOTH LOVE YOU!", "f", (0.62, 0.55))],   # panel, words, m/f, centre as a fraction of it
         labels=[("tl", "SAME DAY", (0.97, 0.06))],                  # panel, words, top-right corner as a fraction
         host="output/channel/art-square.png", out="thumbnail.png")
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
FONT = ROOT / "assets" / "fonts" / "ComicNeue-Bold.ttf"
LABEL_FONT = "/usr/share/fonts/opentype/inter/Inter-BlackItalic.otf"
W, H = 1280, 720
FRAME = (17, 17, 17)
INK = {"m": (22, 50, 230), "f": (232, 22, 160), "n": (20, 20, 20)}
# the three panels: (x, y, w, h) with an 12 px frame and 10 px gutters
PANELS = {"tl": (12, 12, 618, 343), "bl": (12, 365, 618, 343), "r": (640, 12, 628, 696)}


def wrap(text, width):
    rows, cur = [], ""
    for word in text.split():
        if cur and len(cur) + 1 + len(word) > width:
            rows.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    return rows + ([cur] if cur else [])


def words(text, ink, size, width=11):
    """Bold italic capitals, centred rows, on a transparent layer (the italic is a shear of the upright font)."""
    f = ImageFont.truetype(str(FONT), size)
    rows = wrap(text.upper(), width)
    lh = round(size * 1.02)
    tw = round(max(f.getlength(r) for r in rows)) + size
    layer = Image.new("RGBA", (tw, lh * len(rows) + size // 3), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i, r in enumerate(rows):
        x = (tw - f.getlength(r)) / 2
        d.text((x, i * lh), r, font=f, fill=ink + (255,), stroke_width=max(1, size // 28), stroke_fill=ink + (255,))
    k = 0.2  # italic slant
    extra = round(layer.height * k)
    wide = Image.new("RGBA", (layer.width + extra, layer.height), (0, 0, 0, 0))
    wide.paste(layer, (extra, 0))
    return wide.transform(wide.size, Image.AFFINE, (1, k, 0, 0, 1, 0), Image.BICUBIC)


def bubble(img, text, who, cx, cy, size=40, width=11):
    """An oval speech bubble with no tail, centred on (cx, cy)."""
    t = words(text, INK[who], size, width)
    a, b = t.width / 2 * 1.2 + size * 0.45, t.height / 2 * 1.28 + size * 0.45
    d = ImageDraw.Draw(img)
    d.ellipse((cx - a - 4, cy - b - 4, cx + a + 4, cy + b + 4), fill=(0, 0, 0))
    d.ellipse((cx - a, cy - b, cx + a, cy + b), fill=(255, 255, 255))
    img.paste(t, (round(cx - t.width / 2), round(cy - t.height / 2)), t)


def label(img, text, right, top, size=34):
    """A white box with a black border and red capitals; (right, top) is its top-right corner."""
    f = ImageFont.truetype(LABEL_FONT, size)
    tw = f.getlength(text)
    x0, y0 = right - tw - 36, top
    d = ImageDraw.Draw(img)
    d.rectangle((x0, y0, right, y0 + size + 24), fill=(255, 255, 255), outline=(0, 0, 0), width=4)
    d.text((x0 + 18, y0 + 8), text, font=f, fill=(225, 20, 30))


def chibi(img, face, cx, cy, r=62):
    """A round face inset with a white ring, for a comic reaction."""
    face = ImageOps.fit(face.convert("RGB"), (2 * r, 2 * r), Image.LANCZOS)
    m = Image.new("L", face.size, 0)
    ImageDraw.Draw(m).ellipse((0, 0, 2 * r - 1, 2 * r - 1), fill=255)
    d = ImageDraw.Draw(img)
    d.ellipse((cx - r - 7, cy - r - 7, cx + r + 7, cy + r + 7), fill=(0, 0, 0))
    d.ellipse((cx - r - 4, cy - r - 4, cx + r + 4, cy + r + 4), fill=(255, 255, 255))
    img.paste(face, (cx - r, cy - r), m)


def host_corner(img, host, panel="bl", size=150):
    """The host's portrait as a small square in the bottom-left corner of a panel."""
    x, y, w, h = PANELS[panel]
    pic = ImageOps.fit(Image.open(host).convert("RGB"), (size, size), Image.LANCZOS, centering=(0.5, 0.35))
    d = ImageDraw.Draw(img)
    d.rectangle((x + 10, y + h - size - 14, x + size + 14, y + h - 10), fill=(255, 255, 255))
    img.paste(pic, (x + 12, y + h - size - 12))


def page(art, bubbles=(), labels=(), chibis=(), host=None, out="thumbnail.png", focus=None):
    """art: {"tl"|"bl"|"r": image path}; focus: {panel: (fx, fy)} keeps that point of the picture in view.
    bubbles: (panel, words, "m"|"f"|"n", (fx, fy)[, size[, width]]); labels: (panel, words, (fx_right, fy_top));
    chibis: (panel, face image path, crop box in that image, (fx, fy)[, radius])."""
    img = Image.new("RGB", (W, H), FRAME)
    focus = focus or {}
    for k, (x, y, w, h) in PANELS.items():
        pic = ImageOps.fit(Image.open(art[k]).convert("RGB"), (w, h), Image.LANCZOS, centering=focus.get(k, (0.5, 0.5)))
        img.paste(pic, (x, y))
    where = lambda k, fx, fy: (PANELS[k][0] + fx * PANELS[k][2], PANELS[k][1] + fy * PANELS[k][3])
    for k, face, box, (fx, fy), *r in chibis:
        cx, cy = where(k, fx, fy)
        chibi(img, Image.open(face).crop(box), round(cx), round(cy), *r)
    if host:
        host_corner(img, host)
    for k, text, who, (fx, fy), *opt in bubbles:
        bubble(img, text, who, *where(k, fx, fy), *opt)
    for k, text, (fx, fy) in labels:
        label(img, text, *where(k, fx, fy))
    img.save(out)
    return out
