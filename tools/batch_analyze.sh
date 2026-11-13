#!/bin/bash
# Usage: tools/batch_analyze.sh <dossier_videos> <dossier_sortie>
# Analyse (plans + planche) et transcrit chaque vidéo ; reprend là où ça s'est arrêté.
VID=${1:-/home/user/insta/videos}; OUT=${2:-/home/user/insta/an}
T=$(dirname "$0")
export HF_HUB_DISABLE_XET=1
for v in "$VID"/*.mp4; do
  n=$(basename "$v" .mp4)
  [ -f "$OUT/$n/done" ] && continue
  echo "== $n"
  python3 "$T/analyze.py" "$v" "$OUT/$n"
  python3 "$T/transcribe.py" "$v" medium 2>/dev/null > "$OUT/$n/transcript.txt"
  mv "$VID/$n.words.json" "$OUT/$n/" 2>/dev/null
  touch "$OUT/$n/done"
done
echo ALLDONE
