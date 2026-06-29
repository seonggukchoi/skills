#!/usr/bin/env bash
# Extract only scene-change keyframes from a screen-dependent video and build a frame↔timestamp mapping.
#
# Why this script:
#   - Extracting at N-second intervals inflates 12 slides into 600. So it grabs frames only on scene changes.
#   - To avoid manually doing "raise the threshold if there are too many frames, lower it if too few" every time,
#     decode just once at a low threshold to collect every candidate + scene_score (a single decode),
#     and when they exceed the target count, keep only the top N by scene_score and delete the rest.
#   - frames.tsv records each frame's pts_time, [mm:ss], and scene_score, ready to use when writing the document.
#
# Usage:
#   extract_keyframes.sh <video> [out_dir] [max_frames] [low_threshold]
#     video        : input video path (required)
#     out_dir      : frame output directory (default frames)
#     max_frames   : max frames to keep (default 40). If candidates exceed this, keep only the top ones.
#     low_threshold: low scene threshold for first-pass candidate extraction (default 0.12)
#
# Outputs:
#   <out_dir>/NNNN.jpg        keyframes (numbered in time order; deletions may leave gaps in the numbering)
#   <out_dir>/frames.tsv      file<TAB>pts_time<TAB>timestamp<TAB>scene_score (time order)
set -euo pipefail

VIDEO="${1:?Usage: extract_keyframes.sh <video> [out_dir] [max_frames] [low_threshold]}"
OUT="${2:-frames}"
MAX="${3:-40}"
LOW="${4:-0.12}"

[ -f "$VIDEO" ] || { echo "Input video not found: $VIDEO" >&2; exit 1; }
mkdir -p "$OUT"
META="$OUT/_scene_meta.txt"

echo "First pass: scene > $LOW (single decode, collecting candidates + scene_score)"
# metadata=print emits pts_time together with lavfi.scene_score. No showinfo needed.
ffmpeg -nostdin -hide_banner -loglevel error \
  -i "$VIDEO" \
  -vf "select='gt(scene,$LOW)',metadata=print:file=$META" \
  -vsync vfr -q:v 3 "$OUT/%04d.jpg"

echo "Pruning candidates: target max $MAX frames"
python3 - "$OUT" "$META" "$MAX" <<'PY'
import sys, os, re

out, meta, mx = sys.argv[1], sys.argv[2], int(sys.argv[3])

# Parse metadata=print output: "pts_time:12.345" ... "lavfi.scene_score=0.23" pairs
times, scores, cur_t = [], [], None
with open(meta, encoding="utf-8", errors="ignore") as fh:
    for line in fh:
        m = re.search(r'pts_time:([\d.]+)', line)
        if m:
            cur_t = float(m.group(1))
        s = re.search(r'scene_score=([\d.]+)', line)
        if s and cur_t is not None:
            times.append(cur_t)
            scores.append(float(s.group(1)))
            cur_t = None

frames = sorted(f for f in os.listdir(out) if f.lower().endswith(".jpg"))
n = min(len(frames), len(times))
# 1:1 correspondence in extraction order (time order)
items = list(zip(frames[:n], times[:n], scores[:n]))

# When over target, keep only the top mx by scene_score, delete the remaining jpgs
if len(items) > mx:
    keep = {f for f, _, _ in sorted(items, key=lambda x: x[2], reverse=True)[:mx]}
    for f, _, _ in items:
        if f not in keep:
            try:
                os.remove(os.path.join(out, f))
            except OSError:
                pass
    items = [it for it in items if it[0] in keep]

items.sort(key=lambda x: x[1])  # time order
tsv = os.path.join(out, "frames.tsv")
with open(tsv, "w", encoding="utf-8") as w:
    w.write("file\tpts_time\ttimestamp\tscene_score\n")
    for f, t, sc in items:
        w.write(f"{f}\t{t:.3f}\t{int(t//60):02d}:{int(t%60):02d}\t{sc:.3f}\n")

print(f"  kept {len(items)} / candidates {n} (cap {mx}) → {tsv}")
PY

rm -f "$META"
echo "Done: $OUT/  (mapping in $OUT/frames.tsv)"
