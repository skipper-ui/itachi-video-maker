#!/bin/bash
# Re-voice a clip so it sounds like a reference voice, with Seed-VC (zero-shot voice conversion, runs on CPU).
# Only for voices that are AI-generated or belong to the person using it.
#   tools/voice_match.sh SOURCE.wav REFERENCE.wav OUT_DIR
# Words and timing come from SOURCE; the voice comes from REFERENCE. Writes OUT_DIR/vc_*.wav.
set -e
[ $# -eq 3 ] || { echo "usage: $0 SOURCE.wav REFERENCE.wav OUT_DIR" >&2; exit 2; }
SRC=$(realpath "$1"); REF=$(realpath "$2"); mkdir -p "$3"; OUT=$(realpath "$3")
cd ~/seed-vc
HF_HUB_DISABLE_XET=1 exec ~/.venvs/imagegen/bin/python inference.py --source "$SRC" --target "$REF" --output "$OUT" \
  --diffusion-steps 30 --fp16 False
