# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["kokoro-onnx>=0.4.9", "soundfile"]
# ///
"""Local text-to-speech with Kokoro (free, offline).

Reads a script file: one spoken line per paragraph (blank line between
paragraphs). Lines starting with '#' are ignored. Each line is synthesised
separately and joined with a short pause, so line boundaries stay clean beats.

Usage (from anywhere):
  uv run tools/tts.py script.txt -o vo.wav                  # default voice
  uv run tools/tts.py script.txt -o vo.wav --voice am_michael --speed 1.1
  uv run tools/tts.py --list                                # list voice ids
  uv run tools/tts.py --audition "Short test line." -o auditions/   # one wav per voice

Output is 24 kHz mono WAV. Feed it to tools/transcribe.sh for word timings.
"""
import argparse, pathlib, re, sys

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

MODELS = pathlib.Path(__file__).resolve().parent.parent / "models" / "kokoro"
SR = 24000
# A small, good-sounding set for auditions (Kokoro has ~50 voices; see --list).
AUDITION = ["af_heart", "af_bella", "af_nicole", "am_michael", "am_fenrir", "am_puck",
            "bf_emma", "bm_george", "bm_fable"]


def lines(text):
    paras = [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", text)]
    return [p for p in paras if p and not p.startswith("#")]


def speak(k, text, voice, speed, lang):
    audio, sr = k.create(text, voice=voice, speed=speed, lang=lang)
    assert sr == SR, sr
    return audio


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("script", nargs="?", help="text file, one line per paragraph")
    ap.add_argument("-o", "--out", default="vo.wav", help="output wav (or folder for --audition)")
    ap.add_argument("--voice", default="am_michael", help="voice id, or a blend like 'am_michael:60,bm_george:40'")
    ap.add_argument("--speed", type=float, default=1.05)
    ap.add_argument("--lang", default="en-us", help="en-us or en-gb")
    ap.add_argument("--gap", type=float, default=0.45, help="seconds of silence between lines")
    ap.add_argument("--list", action="store_true", help="print available voice ids")
    ap.add_argument("--audition", metavar="TEXT", help="render TEXT once per voice in the audition set")
    a = ap.parse_args()

    k = Kokoro(str(MODELS / "kokoro-v1.0.onnx"), str(MODELS / "voices-v1.0.bin"))
    if a.list:
        print("\n".join(sorted(k.get_voices())))
        return
    if a.audition:
        out = pathlib.Path(a.out)
        out.mkdir(parents=True, exist_ok=True)
        for v in AUDITION:
            lang = "en-gb" if v[0] == "b" else "en-us"
            sf.write(out / f"{v}.wav", speak(k, a.audition, v, a.speed, lang), SR)
            print("  ", out / f"{v}.wav")
        return
    if not a.script:
        ap.error("script file required")

    voice = a.voice
    if ":" in voice:  # weighted blend of style vectors
        parts = [p.split(":") for p in voice.split(",")]
        total = sum(float(w) for _, w in parts)
        voice = sum(k.get_voice_style(v) * (float(w) / total) for v, w in parts)

    gap = np.zeros(int(a.gap * SR), dtype=np.float32)
    chunks = []
    for i, line in enumerate(lines(pathlib.Path(a.script).read_text())):
        print(f"  {i + 1:2d}. {line[:70]}", file=sys.stderr)
        chunks += [speak(k, line, voice, a.speed, a.lang), gap]
    audio = np.concatenate(chunks[:-1])
    sf.write(a.out, audio, SR)
    print(f"{a.out}: {len(audio) / SR:.1f}s")


if __name__ == "__main__":
    main()
