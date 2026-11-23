"""Expressive character lines with Chatterbox TTS (Resemble AI, MIT licence), run in its own environment.

make_video.py calls this for scripts with "emotive" set; it is not imported by the main project, because
Chatterbox needs PyTorch. One-time setup (about 6 GB, outside the repo):

  uv venv --python 3.11 ~/.venvs/chatterbox
  VIRTUAL_ENV=~/.venvs/chatterbox uv pip install chatterbox-tts "setuptools<81"

Usage: ~/.venvs/chatterbox/bin/python tools/emotive_tts.py jobs.json
jobs.json is a list of {"text", "ref" (reference voice wav), "exaggeration", "cfg", "out" (wav to write)}.
The model is downloaded from Hugging Face on first use. Output carries Chatterbox's built-in (inaudible)
Perth watermark.
"""
import json
import os
import sys
import time

os.environ.setdefault("HF_HUB_DISABLE_XET", "1")  # plain HTTPS downloads (the Xet CAS host may be blocked)


def main():
    jobs = json.loads(open(sys.argv[1]).read())
    import torch
    import torchaudio
    from chatterbox.tts import ChatterboxTTS
    torch.set_num_threads(os.cpu_count() or 4)
    model = ChatterboxTTS.from_pretrained(device="cuda" if torch.cuda.is_available() else "cpu")
    t0 = time.time()
    for n, job in enumerate(jobs, 1):
        torch.manual_seed(job.get("seed", 7))
        wav = model.generate(job["text"], audio_prompt_path=job["ref"], exaggeration=job["exaggeration"], cfg_weight=job["cfg"])
        tmp = job["out"] + ".tmp.wav"
        torchaudio.save(tmp, wav, model.sr)
        os.replace(tmp, job["out"])
        print(f"  emotive line {n}/{len(jobs)} done ({time.time() - t0:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
