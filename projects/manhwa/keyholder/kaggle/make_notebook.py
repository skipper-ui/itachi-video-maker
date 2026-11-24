"""Writes keyholder_images.ipynb: a Kaggle notebook that draws the KEYHOLDER scenes still missing an image with
FLUX.2 klein 4B (Apache 2.0, the same model Pollinations used for the first images) on Kaggle's free GPU.

Run: python3 projects/manhwa/keyholder/kaggle/make_notebook.py [scene numbers to redo...]
Scenes without output/manhwa/keyholder/sceneNN.png are included, plus any listed on the command line.
Bring the results back with import_images.py.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
spec = json.loads((HERE.parent / "script.json").read_text())
out_dir = ROOT / "output" / "manhwa" / "keyholder"
redo = {int(a) for a in sys.argv[1:]}
todo = {i: f"{sc['image'].format(character=spec['character'])}, {spec['style']}"
        for i, sc in enumerate(spec["scenes"]) if i in redo or not (out_dir / f"scene{i:02d}.png").exists()}


def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text}


def code(text):
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": text}


cells = [
    md(f"""# KEYHOLDER: scene images with FLUX.2 klein (free Kaggle GPU)

Draws the {len(todo)} remaining scene images for the KEYHOLDER video with **FLUX.2 klein 4B** (Apache 2.0 licence, free
for commercial use), the same model as the first images, so the style matches.

**Before running:** in the right-hand panel, open **Session options** and set
- **Accelerator:** GPU T4 x2 (or GPU P100)
- **Internet:** On (needs a phone-verified Kaggle account)

Then **Run All**. The first run downloads the model (about 15 GB, a few minutes), shows one test image, then draws the
rest (roughly 30-60 seconds each). It skips images that are already done, so if the session stops you can simply
Run All again. When it finishes, download **keyholder_images.zip** from the **Output** panel and send it back."""),
    code('!pip install -q -U "diffusers>=0.37" transformers accelerate'),
    code(f"""import json
W, H = 1920, 1072          # 16:9, divisible by 16
STEPS, GUIDANCE = 4, 1.0   # the model's recommended settings (it is step-distilled)
DTYPE = "auto"             # if the test image comes out black, change to "bfloat16" or "float16" and run again
SCENES = json.loads({json.dumps(json.dumps({f'{i:02d}': p for i, p in todo.items()}, ensure_ascii=False))})
print(len(SCENES), "scenes to draw")"""),
    code("""import torch
from diffusers import Flux2KleinPipeline

major = torch.cuda.get_device_capability()[0]
dtype = {"bfloat16": torch.bfloat16, "float16": torch.float16}.get(DTYPE, torch.bfloat16 if major >= 8 else torch.float16)
print(torch.cuda.get_device_name(0), "->", dtype)
pipe = Flux2KleinPipeline.from_pretrained("black-forest-labs/FLUX.2-klein-4B", torch_dtype=dtype)
pipe.enable_model_cpu_offload()"""),
    code("""import os, time
import numpy as np
os.makedirs("/kaggle/working/images", exist_ok=True)

def draw(num, prompt):
    path = f"/kaggle/working/images/scene{num}.png"
    if os.path.exists(path):
        return path
    for attempt in range(3):
        seed = 1000 + int(num) + 7919 * attempt
        img = pipe(prompt=prompt, width=W, height=H, num_inference_steps=STEPS, guidance_scale=GUIDANCE,
                   generator=torch.Generator(device="cuda").manual_seed(seed)).images[0]
        if np.asarray(img).mean() > 4:   # a black frame means the number format failed; see DTYPE above
            img.save(path)
            return path
        print(f"  scene {num}: black image, retrying")
    raise RuntimeError("Images keep coming out black: change DTYPE in the settings cell and run again.")

first = next(iter(SCENES))
t = time.time()
from IPython.display import Image, display
display(Image(draw(first, SCENES[first]), width=640))
print(f"test image: {time.time() - t:.0f}s")"""),
    code("""t0 = time.time()
for n, (num, prompt) in enumerate(SCENES.items(), 1):
    draw(num, prompt)
    print(f"{n}/{len(SCENES)} scene {num} done ({time.time() - t0:.0f}s)", flush=True)"""),
    code("""import zipfile
with zipfile.ZipFile("/kaggle/working/keyholder_images.zip", "w") as z:
    for f in sorted(os.listdir("/kaggle/working/images")):
        z.write(f"/kaggle/working/images/{f}", f)
print("keyholder_images.zip ready:", len(os.listdir("/kaggle/working/images")), "images. Download it from the Output panel.")"""),
]
colab = [
    md(f"""# KEYHOLDER: scene images with FLUX.2 klein (free Google Colab GPU)

Draws the {len(todo)} remaining scene images with **FLUX.2 klein 4B** (Apache 2.0, free for commercial use), the same
model as the first images. No phone verification needed: just a Google account.

1. **Runtime → Change runtime type → T4 GPU → Save.**
2. **Runtime → Run all.** Allow access to Google Drive when asked: finished images are saved in
   *My Drive/keyholder_images*, so if Colab disconnects, nothing is lost. Just **Run all** again and it carries on.
3. It first reads all the prompts (part 1), then draws the images (part 2, roughly 30-60 seconds each), and shows the
   first one so you can check it. At the end it downloads **keyholder_images.zip**: send that back.

Free Colab machines have little memory, so the model is loaded in two halves, one at a time."""),
    code('!pip install -q -U "diffusers>=0.37" transformers accelerate\n'
         'from google.colab import drive\n'
         'drive.mount("/content/drive")'),
    cells[2]["source"] and code(cells[2]["source"].replace('DTYPE = "auto"             # if the test image comes out black, change to "bfloat16" or "float16" and run again',
                                                          'DTYPE = "float16"          # if images come out black, change to "bfloat16" and Run all again')
                               + '\nOUT = "/content/drive/MyDrive/keyholder_images"'),
    code("""# Part 1: read every prompt with the text model, then unload it.
import os, gc, torch
from diffusers import Flux2KleinPipeline
os.makedirs(OUT, exist_ok=True)
dtype = torch.bfloat16 if DTYPE == "bfloat16" else torch.float16
todo = {n: p for n, p in SCENES.items() if not os.path.exists(f"{OUT}/scene{n}.png")}
print(len(todo), "images left to draw")
embeds = {}
if todo:
    reader = Flux2KleinPipeline.from_pretrained("black-forest-labs/FLUX.2-klein-4B", transformer=None, vae=None, torch_dtype=dtype).to("cuda")
    with torch.no_grad():
        for n, p in todo.items():
            embeds[n] = reader.encode_prompt(prompt=p, device="cuda")[0].cpu()
    del reader; gc.collect(); torch.cuda.empty_cache()
print("prompts ready")"""),
    code("""# Part 2: draw the images with the image model.
import time
import numpy as np
from IPython.display import Image, display
if embeds:
    painter = Flux2KleinPipeline.from_pretrained("black-forest-labs/FLUX.2-klein-4B", text_encoder=None, tokenizer=None, torch_dtype=dtype).to("cuda")
    t0 = time.time()
    for k, (n, e) in enumerate(embeds.items(), 1):
        for attempt in range(3):
            seed = 1000 + int(n) + 7919 * attempt
            img = painter(prompt_embeds=e.to("cuda"), width=W, height=H, num_inference_steps=STEPS, guidance_scale=GUIDANCE,
                          generator=torch.Generator(device="cuda").manual_seed(seed)).images[0]
            if np.asarray(img).mean() > 4:
                break
            print(f"  scene {n}: black image, retrying")
        else:
            raise RuntimeError('Images keep coming out black: set DTYPE = "bfloat16" in the settings cell and Run all again.')
        img.save(f"{OUT}/scene{n}.png")
        if k == 1:
            display(Image(f"{OUT}/scene{n}.png", width=640))
        print(f"{k}/{len(embeds)} scene {n} done ({time.time() - t0:.0f}s)", flush=True)"""),
    code("""import zipfile
from google.colab import files
with zipfile.ZipFile("/content/keyholder_images.zip", "w") as z:
    for f in sorted(os.listdir(OUT)):
        z.write(f"{OUT}/{f}", f)
print(len(os.listdir(OUT)), "images zipped")
files.download("/content/keyholder_images.zip")"""),
]
(HERE / "keyholder_images_colab.ipynb").write_text(json.dumps(
    {"cells": colab, "metadata": {"accelerator": "GPU", "colab": {"gpuType": "T4"}, "kernelspec": {"name": "python3", "display_name": "Python 3"}},
     "nbformat": 4, "nbformat_minor": 5}, indent=1, ensure_ascii=False) + "\n")

nb = {"cells": cells, "metadata": {"kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"},
                                    "language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 5}
(HERE / "keyholder_images.ipynb").write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n")
print(f"{len(todo)} scenes -> keyholder_images.ipynb (Kaggle) and keyholder_images_colab.ipynb (Colab)")
