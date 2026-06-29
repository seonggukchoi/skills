#!/usr/bin/env python3
"""Cut consecutive repeat hallucinations from STT output (SRT).

The Whisper family produces hallucinations that repeat the same phrase dozens to
thousands of times over silent, musical, or applause stretches — e.g., "tire tire tire ..."
running past 1,000 lines near the end of a video. Such runs of identical subtitles carry
no information and get in the way of cross-checking, so when the same text repeats beyond a
threshold count, only the first few are kept and the rest are cut.

This is the first-pass mechanical cleanup right after STT. Meaning-based corrections (proper
nouns, numbers) are judged later by a human/model during the cross-check against the subtitles.

Usage:
    strip_repeats.py input.srt [-o output.srt] [--max-repeat 2] [--report]
      -o/--output    output path (defaults to *.clean.srt next to the input)
      --max-repeat   how many consecutive repeats of the same text to allow (default 2). The excess is dropped.
      --report       print a summary of what was cut, and how much, to stderr

Exit code 0. Check the number of cut blocks with --report.
"""
import argparse
import re
import sys
from pathlib import Path


def parse_srt(text):
    """Parse SRT into a list of (index, timing, text) blocks."""
    blocks = []
    # Blocks separated by blank lines. Normalize newlines to \n.
    raw = re.split(r"\n\s*\n", text.replace("\r\n", "\n").replace("\r", "\n").strip())
    for chunk in raw:
        lines = chunk.split("\n")
        if len(lines) < 2:
            continue
        idx = lines[0].strip()
        timing = lines[1].strip()
        body = "\n".join(lines[2:]).strip()
        blocks.append((idx, timing, body))
    return blocks


def norm(s):
    """Normalize for comparison: collapse whitespace and lowercase."""
    return re.sub(r"\s+", " ", s).strip().lower()


def strip_repeats(blocks, max_repeat):
    """Drop the excess when consecutive identical text exceeds max_repeat."""
    out, dropped = [], 0
    run_key, run_n = None, 0
    for idx, timing, body in blocks:
        key = norm(body)
        if key and key == run_key:
            run_n += 1
        else:
            run_key, run_n = key, 1
        if run_n <= max_repeat or not key:
            out.append((idx, timing, body))
        else:
            dropped += 1
    return out, dropped


def to_srt(blocks):
    """Reindex blocks from 1 and serialize into an SRT string."""
    parts = []
    for i, (_, timing, body) in enumerate(blocks, 1):
        parts.append(f"{i}\n{timing}\n{body}")
    return "\n\n".join(parts) + "\n"


def main():
    ap = argparse.ArgumentParser(description="Cut consecutive repeat hallucinations from an STT SRT")
    ap.add_argument("input", help="input SRT path")
    ap.add_argument("-o", "--output", help="output path (default: *.clean.srt)")
    ap.add_argument("--max-repeat", type=int, default=2, help="consecutive repeats allowed (default 2)")
    ap.add_argument("--report", action="store_true", help="print a summary to stderr")
    args = ap.parse_args()

    src = Path(args.input)
    if not src.is_file():
        print(f"Input not found: {src}", file=sys.stderr)
        sys.exit(1)

    text = src.read_text(encoding="utf-8", errors="ignore")
    blocks = parse_srt(text)
    kept, dropped = strip_repeats(blocks, args.max_repeat)

    out_path = Path(args.output) if args.output else src.with_suffix(".clean.srt")
    out_path.write_text(to_srt(kept), encoding="utf-8")

    if args.report:
        print(
            f"strip_repeats: blocks {len(blocks)} → {len(kept)} "
            f"({dropped} repeat hallucinations removed, max-repeat={args.max_repeat})",
            file=sys.stderr,
        )
    print(str(out_path))


if __name__ == "__main__":
    main()
