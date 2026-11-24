"""Brings the Kaggle notebook's images into the KEYHOLDER output folder so make_video.py uses them as they are.

Run: uv run python projects/manhwa/keyholder/kaggle/import_images.py path/to/keyholder_images.zip
Each sceneNN.png is copied in and stamped with the cache key make_video.py expects for that scene's prompt,
so it is treated as up to date instead of being drawn again.
"""
import json
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
import make_video as mv  # noqa: E402

spec = json.loads((HERE.parent / "script.json").read_text())
out_dir = ROOT / "output" / "manhwa" / "keyholder"
out_dir.mkdir(parents=True, exist_ok=True)
provider = spec.get("images", {}).get("provider", "pollinations")
model = {"fal": mv.IMAGE_MODEL, "pollinations": mv.POLLINATIONS_MODEL}.get(provider, (mv.MH_MODEL, mv.MH_RESOLUTION))
with tempfile.TemporaryDirectory() as tmp:
    zipfile.ZipFile(sys.argv[1]).extractall(tmp)
    n = 0
    for f in sorted(Path(tmp).rglob("scene*.png")):
        i = int(f.stem[5:])
        prompt = f"{spec['scenes'][i]['image'].format(character=spec['character'])}, {spec['style']}"
        dest = out_dir / f"scene{i:02d}.png"
        shutil.copy(f, dest)
        mv.mark(dest, mv.fingerprint(prompt, spec.get("width", 1920), spec.get("height", 1080), provider, model))
        n += 1
print(f"imported {n} images into {out_dir}")
