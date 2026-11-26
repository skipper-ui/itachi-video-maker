#!/bin/bash
# Re-voice a clip so it sounds like a reference voice, with Seed-VC (zero-shot voice conversion, runs on CPU).
# Only for voices that are AI-generated or belong to the person using it.
#   tools/voice_match.sh SOURCE.wav REFERENCE.wav OUT_DIR [v1|v2|v2style]
# Words and timing come from SOURCE; the voice comes from REFERENCE. v2 (default) is Seed-VC's newer model, closer to
# the reference voice; v1 is the original model. Writes the converted wav into OUT_DIR.
set -e
[ $# -ge 3 ] || { echo "usage: $0 SOURCE.wav REFERENCE.wav OUT_DIR [v1|v2|v2style]" >&2; exit 2; }
SRC=$(realpath "$1"); REF=$(realpath "$2"); mkdir -p "$3"; OUT=$(realpath "$3")
cd ~/seed-vc
export HF_HUB_DISABLE_XET=1
if [ "${4:-v2}" = v1 ]; then
  exec ~/.venvs/imagegen/bin/python inference.py --source "$SRC" --target "$REF" --output "$OUT" --diffusion-steps 30 --fp16 False
fi
# v2style also copies the reference's way of speaking (accent, emotion); the timing then changes slightly
STYLE=false; [ "${4:-v2}" = v2style ] && STYLE=true
exec ~/.venvs/imagegen/bin/python inference_v2.py --source "$SRC" --target "$REF" --output "$OUT" --diffusion-steps 50 \
  --similarity-cfg-rate 1.0 --intelligibility-cfg-rate 0.7 --convert-style $STYLE
