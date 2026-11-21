# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pillow"]
# ///
"""Shaded-relief texture for a map region, in the region's own projection.

  uv run tools/geo/relief.py <region.json> [...]     # writes <region>.relief.jpg next to each

Reads Natural Earth SR_50M (run tools/geo/fetch.sh once). The output is a 2x-resolution (2160x2000)
grayscale JPEG centred on mid-grey, so a CSS `mix-blend-mode: overlay` adds terrain to whatever
colours the map paths have, and leaves flat land and sea unchanged. 1:50m is ~3.7 km per pixel:
sharp at continent and country scale, soft when zoomed into a single state.
"""
import json, math, pathlib, sys
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
SRC = pathlib.Path(__file__).resolve().parent / "data" / "SR_50M.tif"
K = 2   # supersample: the camera zooms up to ~2x


def build(region_json, sr):
    g = json.loads(region_json.read_text())
    p, W, H = g["proj"], g["W"] * K, g["H"] * K
    x = (np.arange(W) + 0.5) / K
    y = (np.arange(H) + 0.5) / K
    lon = np.degrees((x - p["tx"]) / p["scale"])
    lat = np.degrees(2 * np.arctan(np.exp((p["ty"] - y) / p["scale"])) - math.pi / 2)
    sh, sw = sr.shape
    col = np.clip(((lon + 180) / 360 * sw).astype(int), 0, sw - 1)
    row = np.clip(((90 - lat) / 180 * sh).astype(int), 0, sh - 1)
    img = sr[row[:, None], col[None, :]].astype(np.float32)
    # flat ground in SR_50M is light grey: re-centre on 128 and boost relief contrast
    img = np.clip(128 + (img - np.median(img)) * 1.6, 0, 255).astype(np.uint8)
    out = region_json.with_suffix(".relief.jpg")
    Image.fromarray(img, "L").save(out, quality=82, optimize=True)
    print(f"{out}: {W}x{H}, {out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    if not SRC.exists():
        raise SystemExit(f"missing {SRC}: run tools/geo/fetch.sh")
    sr = np.asarray(Image.open(SRC).convert("L"))
    for a in sys.argv[1:]:
        build(pathlib.Path(a), sr)
