"""Draw scene images with FLUX.2 klein 4B (Apache 2.0) on this machine's CPU, no GPU or paid service needed.

The model is loaded in two halves so it fits in ~15 GB of RAM: first the text encoder turns every prompt into
embeddings (saved next to the output), then it is unloaded and the image model draws from those embeddings.
bf16 weights use the CPU's AMX/AVX-512 BF16 units where available.

Run in its own environment (torch, diffusers>=0.37, transformers, accelerate):
  ~/.venvs/imagegen/bin/python tools/flux_local.py SCRIPT.json OUT_DIR [--size 1024x576] [--scenes 45,46,...]
Images are written as OUT_DIR/sceneNN.png (existing ones are skipped, so it can be stopped and resumed).
"""
import argparse
import gc
import json
import os
import time
from pathlib import Path

os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
MODEL = "black-forest-labs/FLUX.2-klein-4B"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--size", default="1024x576")
    ap.add_argument("--scenes", default="")
    args = ap.parse_args()
    import torch
    from diffusers import Flux2KleinPipeline
    torch.set_num_threads(os.cpu_count() or 4)
    w, h = map(int, args.size.split("x"))
    spec = json.loads(args.script.read_text())
    wanted = {int(s) for s in args.scenes.split(",") if s} or set(range(len(spec["scenes"])))
    todo = {i: f"{sc['image'].format(character=spec.get('character', ''))}, {spec.get('style', '')}"
            for i, sc in enumerate(spec["scenes"]) if i in wanted and not (args.out / f"scene{i:02d}.png").exists()}
    if not todo:
        return print("nothing to draw")
    emb_dir = args.out / "flux_embeds"
    emb_dir.mkdir(parents=True, exist_ok=True)

    need = [i for i in todo if not (emb_dir / f"{i:02d}.pt").exists()]
    if need:
        t0 = time.time()
        reader = Flux2KleinPipeline.from_pretrained(MODEL, transformer=None, vae=None, torch_dtype=torch.bfloat16)
        with torch.inference_mode():
            for n, i in enumerate(need, 1):
                emb = reader.encode_prompt(prompt=todo[i], device="cpu")[0]
                torch.save(emb.clone(), emb_dir / f"{i:02d}.pt")
                print(f"  prompt {n}/{len(need)} read ({time.time() - t0:.0f}s)", flush=True)
        del reader
        gc.collect()

    painter = Flux2KleinPipeline.from_pretrained(MODEL, text_encoder=None, tokenizer=None, torch_dtype=torch.bfloat16)
    t0 = time.time()
    with torch.inference_mode():
        for n, i in enumerate(todo, 1):
            emb = torch.load(emb_dir / f"{i:02d}.pt")
            img = painter(prompt_embeds=emb, width=w, height=h, num_inference_steps=4, guidance_scale=1.0,
                          generator=torch.Generator().manual_seed(1000 + i)).images[0]
            tmp = args.out / f"scene{i:02d}.tmp.png"
            img.save(tmp)
            os.replace(tmp, args.out / f"scene{i:02d}.png")
            print(f"  image {n}/{len(todo)} scene {i} drawn ({time.time() - t0:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
