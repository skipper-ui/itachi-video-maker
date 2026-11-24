"""Upscale AI images 4x with an anime-trained Real-ESRGAN model, run in the Chatterbox environment (PyTorch).

make_video.py calls this for scripts with "images": {"upscale": true}, so 640px images from a free image plan
come out crisp at 1080p. One-time setup (outside the repo):

  VIRTUAL_ENV=~/.venvs/chatterbox uv pip install spandrel
  mkdir -p ~/models && curl -L -o ~/models/RealESRGAN_x4plus_anime_6B.pth \\
    https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x4plus_anime_6B.pth

Usage: ~/.venvs/chatterbox/bin/python tools/upscale.py MODEL.pth IMAGE.png [IMAGE.png ...]   (overwrites each image)
"""
import os
import sys
import time


def main():
    import numpy as np
    import torch
    from PIL import Image
    from spandrel import ModelLoader
    torch.set_num_threads(os.cpu_count() or 4)
    model = ModelLoader().load_from_file(sys.argv[1]).eval()
    t0 = time.time()
    for n, path in enumerate(sys.argv[2:], 1):
        im = np.asarray(Image.open(path).convert("RGB")).astype("float32") / 255
        with torch.no_grad():
            out = model(torch.from_numpy(im).permute(2, 0, 1)[None])
        out = (out[0].permute(1, 2, 0).clamp(0, 1).numpy() * 255).round().astype("uint8")
        tmp = path + ".tmp.png"
        Image.fromarray(out).save(tmp)
        os.replace(tmp, path)
        print(f"  upscaled {n}/{len(sys.argv) - 2} ({time.time() - t0:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
