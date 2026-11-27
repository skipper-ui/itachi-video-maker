"""Comic-page YouTube thumbnail (1280x720) for FUTARI, in the channel's house style (projects/manga/STYLE.md).

  python3 projects/manga/futari/thumbnail.py          # draw the three panels (local FLUX.2 klein + Real-ESRGAN), then lay out
  python3 projects/manga/futari/thumbnail.py text     # only redo the bubbles and layout over the art already drawn

Panels: top-left, her "I'm at my parents'" lie and the mall; bottom-left, Ren heartbroken (with Hana in the corner);
right, the twins. The art uses the video's character portraits, so the faces match the video.
Output: output/manga/futari/thumb/thumbnail.png
"""
import contextlib
import io
import json
import os
import runpy
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "output" / "manga" / "futari" / "thumb"
PY = Path.home() / ".venvs" / "imagegen" / "bin" / "python"
ESRGAN = Path.home() / "models" / "RealESRGAN_x4plus_anime_6B.pth"
sys.path.insert(0, str(ROOT / "tools"))

with contextlib.redirect_stdout(io.StringIO()):  # the video's characters and style (build.py also rewrites script.json)
    B = runpy.run_path(str(HERE / "build.py"))
C, REFS, STYLE = B["C"], B["REFS"], B["STYLE"] + ", vibrant colors, glossy, dramatic lighting"

# (prompt, size) for each panel; the right panel is tall
ART = {
    "tl": ("{TWIN} smiling happily and hugging the arm of {KAITO} as they walk through a bright shopping mall, "
           "both seen from the waist up, their faces in the upper middle of the picture", "1024x576"),
    "bl": ("close-up of {REN} heartbroken at night, tears running down his face, staring at his phone in disbelief, "
           "his face on the right half of the picture, dark city street with blurred lights", "1024x576"),
    "r": ("close-up of {TWIN_AKARI} on the left and {TWIN_HIKARI} on the right, side by side, leaning toward the "
          "viewer, both blushing with determined smiles, their faces in the upper half of the picture, "
          "a sunny mikan orchard with green trees and orange fruits and the blue sea behind them, summer", "768x848"),
}


def draw():
    spec = json.loads((HERE / "script.json").read_text())
    (OUT / "refs").mkdir(parents=True, exist_ok=True)
    for f in (ROOT / "output" / "manga" / "futari" / "refs").glob("*.png"):
        if not (OUT / "refs" / f.name).exists():
            shutil.copy(f, OUT / "refs" / f.name)
    for k, (prompt, size) in ART.items():
        art = OUT / f"art-{k}.png"
        if art.exists():
            continue
        work = OUT / k
        work.mkdir(exist_ok=True)
        if not (work / "refs").exists():
            shutil.copytree(OUT / "refs", work / "refs")
        import re
        refs = sorted({REFS[n] for n in re.findall(r"\{(\w+)\}", prompt)})
        script = work / "script.json"
        script.write_text(json.dumps({"style": STYLE, "characters": spec["characters"],
                                      "scenes": [{"image": prompt.format(**C) + ", " + STYLE, "refs": refs}] * 3},
                                     indent=1))
        subprocess.run([str(PY), str(ROOT / "tools" / "flux_local.py"), str(script), str(work), "--size", size,
                        "--seed", os.environ.get("SEED", "8100")], check=True, cwd=ROOT)
    # three tries per panel are drawn; the chosen one is copied to art-<panel>.png by hand (see PICK) and upscaled
    for k, n in PICK.items():
        art = OUT / f"art-{k}.png"
        if not art.exists() and (OUT / k / f"scene{n:02d}.png").exists():
            shutil.copy(OUT / k / f"scene{n:02d}.png", art)
            subprocess.run([str(PY), str(ROOT / "tools" / "upscale.py"), str(ESRGAN), str(art)], check=True, cwd=ROOT)


PICK = {"tl": 0, "bl": 0, "r": 0}  # which of the three tries to use for each panel


def text():
    from comic_thumb import page
    page({k: OUT / f"art-{k}.png" for k in ART},
         bubbles=[("tl", "I'M AT MY PARENTS' TODAY!", "f", (0.2, 0.62), 34, 10),
                  ("bl", "SHE LIED TO ME...", "m", (0.3, 0.3), 38, 9),
                  ("r", "THERE'S TWO OF HER?!", "m", (0.3, 0.09), 36, 12),
                  ("r", "WE BOTH LOVE YOU!", "f", (0.76, 0.6), 38, 9),
                  ("r", "NOW CHOOSE ONE!", "f", (0.27, 0.84), 38, 9)],
         labels=[("tl", "SAME DAY...", (0.975, 0.05)), ("r", "TWINS", (0.975, 0.2))],
         host=ROOT / "output" / "channel" / "art-square.png", out=OUT / "thumbnail.png",
         focus={"tl": (0.5, 0.3), "bl": (0.6, 0.4), "r": (0.5, 0.3)})
    print(OUT / "thumbnail.png")


if __name__ == "__main__":
    if sys.argv[1:] != ["text"]:
        draw()
    if all((OUT / f"art-{k}.png").exists() for k in ART):
        text()
