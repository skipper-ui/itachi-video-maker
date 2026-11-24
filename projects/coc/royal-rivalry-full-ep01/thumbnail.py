"""Builds thumbnail.json and renders thumbnail.png (1280x720) for The Royal Rivalry, Episode 1.

Run: python3 projects/coc/royal-rivalry-full-ep01/thumbnail.py
The page is drawn by the comic engine (thumbnail.html overrides it to full bleed); official art is only placed
and scaled. Variants: pass a name to render one of VARIANTS.
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent))
from rivalry import A, S, P, Cap  # noqa: E402

def scene(titles, sfx=(), caps=()):
    return {"lines": [], "page": {"layout": "1", "titles": list(titles), "panels": [P(
        "storm",
        under=["glow:0.2,0.6,820,255,140,40", "glow:0.2,0.6,520,255,170,60", "glow:0.82,0.6,820,180,90,255", "glow:0.82,0.6,520,200,120,255"],
        fx=["bolt:0.5,-0.05,0.5,1.05,1,22@0", "eyes:0.5,0.1,0.045,120,210,255@0"],
        art=[A("king_charge", .24, .66, 1.25), A("queen_aim", .77, .66, 1.25)],
        sfx=list(sfx), caps=list(caps))]}}

VARIANTS = {
    "a": scene([{"text": "WHO WINS?", "y": 0.84, "size": 190, "rot": -0.03}],
               sfx=[S("VS", .5, .5, 0, style="red", size=230)], caps=[Cap("EPISODE 1", x=.025, y=.04, size=48)]),
    "b": scene([{"text": "ONLY ONE", "y": 0.8, "size": 200, "rot": -0.03}, {"text": "CAN WIN", "y": 0.93, "size": 110, "style": "white", "rot": -0.03}],
               caps=[Cap("EPISODE 1", x=.025, y=.04, size=48)]),
}

def render(name):
    (HERE / "thumbnail.json").write_text(json.dumps({"scenes": [VARIANTS[name]]}, indent=1) + "\n")
    out = HERE / f"thumbnail-{name}.mp4"
    subprocess.run(["node", str(ROOT / "motion" / "render.js"), str(HERE / "thumbnail.html"), "0", "3", "30", str(out), "--stills", "2.5"], check=True)
    still = sorted(HERE.glob(f"thumbnail-{name}*.png"))[-1]
    final = ROOT / "output" / "coc" / "royal-rivalry-full-ep01" / f"thumbnail-{name}.png"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(still), "-vf", "scale=1280:720:flags=lanczos", str(final)], check=True)
    still.unlink()
    print(final)

for n in (sys.argv[1:] or VARIANTS):
    render(n)
