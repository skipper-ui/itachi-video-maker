"""Animate scene images into short video shots with LTX-Video 2B 0.9.8 distilled (open weights) on this machine's CPU.

Like flux_local.py, the model is used in two halves so it fits in ~15 GB of RAM: first the T5 text encoder turns every
motion prompt into embeddings (saved next to the output), then it is unloaded and the video model animates each image.

  ~/.venvs/imagegen/bin/python tools/ltx_local.py SCRIPT.json IMAGES_DIR OUT_DIR MOTIONS.json [--scenes 1,39]
      [--size 768x448] [--frames 97] [--seed 2000]

MOTIONS.json maps scene numbers to a description of the movement ("her ponytail blows in the wind as she turns...").
The scene's image prompt is added after it, so the model knows what it is looking at. Shots are written as
OUT_DIR/sceneNN.mp4 at 24 fps; existing ones are skipped, so it can be stopped and resumed.
With --fit-audio, each shot is made as long as IMAGES_DIR/sceneNN.mp3: after the first 4 seconds the model carries
on from the last 9 frames it drew, part by part (saved in OUT_DIR/parts, so a stopped run resumes mid-scene).
"""
import argparse
import gc
import json
import os
import subprocess
import time
from pathlib import Path

os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
REPO = "Lightricks/LTX-Video"
CONFIG = "Lightricks/LTX-Video-0.9.5"
WEIGHTS = "ltxv-2b-0.9.8-distilled.safetensors"
T5 = "city96/t5-v1_1-xxl-encoder-bf16"
# the distilled model's own 8-step schedule
TIMESTEPS = [1000, 993, 987, 981, 975, 909, 725, 0.03]
NEGATIVE = "worst quality, inconsistent motion, blurry, jittery, distorted, deformed face, extra limbs, morphing"


def fit(img, w, h):
    """Scale and centre-crop a PIL image to exactly w x h."""
    from PIL import Image
    s = max(w / img.width, h / img.height)
    img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x, y = (img.width - w) // 2, (img.height - h) // 2
    return img.crop((x, y, x + w, y + h))


def save_mp4(frames, path, fps=24):
    w, h = frames[0].size
    tmp = path.with_suffix(".tmp.mp4")
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
                          "-r", str(fps), "-i", "-", "-c:v", "libx264", "-crf", "14", "-preset", "medium",
                          "-pix_fmt", "yuv420p", str(tmp)], stdin=subprocess.PIPE)
    for f in frames:
        p.stdin.write(f.convert("RGB").tobytes())
    p.stdin.close()
    if p.wait():
        raise RuntimeError(f"ffmpeg failed writing {path}")
    os.replace(tmp, path)


OVERLAP = 9  # frames each continuation part re-uses from the end of the previous one


def duration(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                                capture_output=True, text=True, check=True).stdout)


def read_frames(path, last=None):
    from PIL import Image
    w, h = map(int, subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                                    "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True).stdout.split(","))
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    frames = [Image.frombytes("RGB", (w, h), raw[i:i + w * h * 3]) for i in range(0, len(raw), w * h * 3)]
    return frames[-last:] if last else frames


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script", type=Path)
    ap.add_argument("images", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("motions", type=Path)
    ap.add_argument("--scenes", default="")
    ap.add_argument("--size", default="768x448")
    ap.add_argument("--frames", type=int, default=97, help="8k+1 frames at 24 fps (97 = 4 s)")
    ap.add_argument("--seed", type=int, default=2000)
    ap.add_argument("--fit-audio", action="store_true", help="extend each shot to the length of its sceneNN.mp3")
    ap.add_argument("--anchor", type=float, default=0.8, help="how strongly continuation parts return to the scene image")
    ap.add_argument("--pin-ends", action="store_true", help="steer the first part back to the scene image too")
    ap.add_argument("--tail", type=float, default=0.95, help="seconds added after the audio (make_video's scene pad + crossfade)")
    args = ap.parse_args()
    import torch
    from PIL import Image
    from diffusers import AutoencoderKLLTXVideo, FlowMatchEulerDiscreteScheduler, LTXConditionPipeline, LTXVideoTransformer3DModel
    from diffusers.pipelines.ltx.pipeline_ltx_condition import LTXVideoCondition
    from huggingface_hub import hf_hub_download
    from transformers import T5EncoderModel, T5TokenizerFast
    torch.set_num_threads(os.cpu_count() or 4)
    w, h = map(int, args.size.split("x"))
    spec = json.loads(args.script.read_text())
    motions = {int(k): v for k, v in json.loads(args.motions.read_text()).items()}
    wanted = {int(s) for s in args.scenes.split(",") if s} or set(motions)
    todo = {}
    for i in sorted(wanted):
        if (args.out / f"scene{i:02d}.mp4").exists():
            continue
        look = spec["scenes"][i]["image"].format(character=spec.get("character", "")).split(", Korean manhwa")[0]
        todo[i] = f"{motions[i]} {look}. Smooth fluid 2D anime animation, Korean manhwa webtoon style, cinematic."
    if not todo:
        return print("nothing to animate")
    emb_dir = args.out / "ltx_embeds"
    emb_dir.mkdir(parents=True, exist_ok=True)

    scheduler = FlowMatchEulerDiscreteScheduler.from_pretrained(CONFIG, subfolder="scheduler")
    need = [i for i in todo if not (emb_dir / f"{i:02d}.pt").exists()]
    if need:
        t0 = time.time()
        reader = LTXConditionPipeline(scheduler=scheduler, vae=None, transformer=None,
                                      text_encoder=T5EncoderModel.from_pretrained(T5, torch_dtype=torch.bfloat16),
                                      tokenizer=T5TokenizerFast.from_pretrained(CONFIG, subfolder="tokenizer"))
        with torch.inference_mode():
            for n, i in enumerate(need, 1):
                pe, pm, ne, nm = reader.encode_prompt(prompt=todo[i], negative_prompt=NEGATIVE, do_classifier_free_guidance=True,
                                                      max_sequence_length=256, device="cpu")
                torch.save({"pe": pe.clone(), "pm": pm.clone(), "ne": ne.clone(), "nm": nm.clone()}, emb_dir / f"{i:02d}.pt")
                print(f"  prompt {n}/{len(need)} read ({time.time() - t0:.0f}s)", flush=True)
        del reader
        gc.collect()

    weights = hf_hub_download(REPO, WEIGHTS)
    t0 = time.time()
    transformer = LTXVideoTransformer3DModel.from_single_file(weights, config=CONFIG, subfolder="transformer", torch_dtype=torch.bfloat16)
    vae = AutoencoderKLLTXVideo.from_single_file(weights, config=CONFIG, subfolder="vae", torch_dtype=torch.bfloat16)
    painter = LTXConditionPipeline(scheduler=scheduler, vae=vae, transformer=transformer, text_encoder=None, tokenizer=None)
    painter.vae.enable_tiling()
    print(f"  video model loaded ({time.time() - t0:.0f}s)", flush=True)
    parts_dir = args.out / "parts"
    parts_dir.mkdir(parents=True, exist_ok=True)

    def draw(i, part, cond):
        e = torch.load(emb_dir / f"{i:02d}.pt")
        with torch.inference_mode():
            return painter(conditions=cond if isinstance(cond, list) else [cond], prompt_embeds=e["pe"], prompt_attention_mask=e["pm"],
                           negative_prompt_embeds=e["ne"], negative_prompt_attention_mask=e["nm"],
                           width=w, height=h, num_frames=args.frames, frame_rate=24, timesteps=TIMESTEPS,
                           guidance_scale=1.0, decode_timestep=0.05, decode_noise_scale=0.025, image_cond_noise_scale=0.0,
                           generator=torch.Generator().manual_seed(args.seed + i + 7919 * part)).frames[0]

    for n, i in enumerate(todo, 1):
        t0 = time.time()
        need = args.frames
        if args.fit_audio:
            need = max(args.frames, int((duration(args.images / f"scene{i:02d}.mp3") + args.tail) * 24) + 1)
        step = args.frames - OVERLAP
        count = 1 + max(0, -(-(need - args.frames) // step))
        frames = []
        for k in range(count):
            part = parts_dir / f"scene{i:02d}-{k}.mp4"
            if not part.exists():
                if k == 0:
                    still = fit(Image.open(args.images / f"scene{i:02d}.png").convert("RGB"), w, h)
                    cond = [LTXVideoCondition(image=still, frame_index=0)]
                    if args.pin_ends:  # also return to the picture at the end, so nothing drifts mid-shot
                        cond.append(LTXVideoCondition(image=still, frame_index=(args.frames - 1) // 8 * 8, strength=args.anchor))
                else:
                    # carry on from the previous part, and steer back to the original picture by the end of this one
                    # so the characters and framing don't drift further with every part
                    still = fit(Image.open(args.images / f"scene{i:02d}.png").convert("RGB"), w, h)
                    cond = [LTXVideoCondition(video=read_frames(parts_dir / f"scene{i:02d}-{k - 1}.mp4", OVERLAP), frame_index=0),
                            LTXVideoCondition(image=still, frame_index=(args.frames - 1) // 8 * 8, strength=args.anchor)]
                save_mp4(draw(i, k, cond), part)
                print(f"    scene {i} part {k + 1}/{count} ({time.time() - t0:.0f}s)", flush=True)
            got = read_frames(part)
            frames += got if k == 0 else got[OVERLAP:]
        save_mp4(frames[:need], args.out / f"scene{i:02d}.mp4")
        print(f"  shot {n}/{len(todo)} scene {i} animated, {need / 24:.1f}s ({time.time() - t0:.0f}s)", flush=True)

if __name__ == "__main__":
    main()
