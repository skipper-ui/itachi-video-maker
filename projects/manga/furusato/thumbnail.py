"""YouTube thumbnails (1280x720) for FURUSATO, two variants to A/B test.

  python3 projects/manga/furusato/thumbnail.py          # draw the art (local FLUX.2 klein + Real-ESRGAN), then add text
  python3 projects/manga/furusato/thumbnail.py text     # only redo the text over the art already drawn

The art reuses the video's character portraits as references, so the faces match the video.
Output: output/manga/furusato/thumb/thumbnail-a.png and thumbnail-b.png
"""
import ast
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "output" / "manga" / "furusato" / "thumb"
PY = Path.home() / ".venvs" / "imagegen" / "bin" / "python"
ESRGAN = Path.home() / "models" / "RealESRGAN_x4plus_anime_6B.pth"
FONT = "/usr/share/fonts/opentype/inter/Inter-BlackItalic.otf"

# the character descriptions used for the video, read from build.py without running it
C = next(ast.literal_eval(n.value) for n in ast.parse((HERE / "build.py").read_text()).body
         if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "C")

ART = {
    "a": ("{HARUTO} in the left foreground with tears in his eyes and a shocked, heartbroken face, holding a crushed "
          "strawberry cake box; behind him on the right {DAICHI} smirks smugly with his arm around the waist of {ERIKA}, "
          "who leans on him with a cold smile; dramatic lighting, dark city apartment at night, close-up, emotional",
          ["haruto", "daichi", "erika"]),
    "b": ("{HARUTO_HOME} standing in the centre-left, smiling confidently and holding up a modern clay-pot-style rice "
          "cooker with a wooden lid, warm golden sunlight, mountain workshop behind him; on the far right, small in the "
          "background, {DAICHI} and {ERIKA} stare at him in total shock with their jaws dropped",
          ["haruto", "daichi", "erika"]),
}
# (text, colour, size, y) lines per variant; x is set per variant so the words sit away from the faces
TEXT = {
    "a": {"x": 0.97, "align": "right", "y": 0.05, "lines": [("MY BEST FRIEND", "#FFFFFF", 92), ("TOOK", "#FFD43B", 120),
                                                         ("EVERYTHING", "#FFD43B", 120)]},
    "b": {"x": 0.03, "align": "left", "y": 0.05, "lines": [("THEY LAUGHED...", "#FFFFFF", 96), ("THEN I", "#FFD43B", 116),
                                                        ("CAME BACK", "#FFD43B", 116)]},
}


def draw():
    spec = json.loads((HERE / "script.json").read_text())
    scenes = [{"image": ART[k][0].format(**C), "refs": ART[k][1]} for k in sorted(ART)]
    (OUT / "refs").mkdir(parents=True, exist_ok=True)
    for r in {r for k in ART for r in ART[k][1]}:  # same portraits as the video
        src = ROOT / "output" / "manga" / "furusato" / "refs" / f"{r}.png"
        if not (OUT / "refs" / f"{r}.png").exists():
            shutil.copy(src, OUT / "refs" / f"{r}.png")
    script = OUT / "thumb_script.json"
    script.write_text(json.dumps({"style": spec["style"], "characters": {r: spec["characters"][r] for k in ART for r in ART[k][1]}, "scenes": scenes}, indent=1))
    subprocess.run([str(PY), str(ROOT / "tools" / "flux_local.py"), str(script), str(OUT), "--size", "1024x576",
                    "--seed", os.environ.get("SEED", "4200")], check=True, cwd=ROOT)
    for i, k in enumerate(sorted(ART)):
        art = OUT / f"art-{k}.png"
        if not art.exists():
            shutil.copy(OUT / f"scene{i:02d}.png", art)
            subprocess.run([str(PY), str(ROOT / "tools" / "upscale.py"), str(ESRGAN), str(art)], check=True, cwd=ROOT)


def text():
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
    for k, t in TEXT.items():
        img = Image.open(OUT / f"art-{k}.png").convert("RGB").resize((1280, 720), Image.LANCZOS)
        # darken the corner the words sit in, so they pop
        shade = Image.new("L", (1280, 720), 0)
        sd = ImageDraw.Draw(shade)
        cx = 1280 if t["align"] == "right" else 0
        sd.ellipse((cx - 700, -330, cx + 700, 420), fill=170)
        img = Image.composite(Image.new("RGB", img.size, (0, 0, 0)), img, shade.filter(ImageFilter.GaussianBlur(90)))
        d = ImageDraw.Draw(img)
        y = t["y"] * 720
        for words, colour, size in t["lines"]:
            f = ImageFont.truetype(FONT, size)
            w = d.textlength(words, font=f)
            x = t["x"] * 1280 - (w if t["align"] == "right" else 0)
            d.text((x + 6, y + 8), words, font=f, fill="#000000", stroke_width=12, stroke_fill="#000000")  # drop shadow
            d.text((x, y), words, font=f, fill=colour, stroke_width=10, stroke_fill="#000000")
            y += size * 1.02
        # "MANGA DUB" tag in the opposite bottom corner
        f = ImageFont.truetype(FONT, 40)
        tag = "MANGA DUB"
        tw = d.textlength(tag, font=f)
        bx = 28 if t["align"] == "right" else 1280 - tw - 60
        d.rounded_rectangle((bx, 640, bx + tw + 32, 700), 10, fill="#E62117", outline="#000000", width=4)
        d.text((bx + 16, 646), tag, font=f, fill="#FFFFFF")
        out = OUT / f"thumbnail-{k}.png"
        img.save(out)
        print(out)


if __name__ == "__main__":
    if sys.argv[1:] != ["text"]:
        draw()
    text()
