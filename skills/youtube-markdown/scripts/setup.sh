#!/usr/bin/env bash
# youtube-markdown setup — idempotent. Skips anything already installed.
#
# Key lesson: don't check whether mlx-whisper works with `python -c "import mlx_whisper"`.
# mlx-whisper is often installed into an isolated environment such as uv tool, so even though
# the import fails under the system python, the CLI (`mlx_whisper`) works fine. So always verify by CLI presence.
set -euo pipefail

echo "[1/3] ffmpeg, yt-dlp (Homebrew)"
for pkg in ffmpeg yt-dlp; do
  if command -v "$pkg" >/dev/null 2>&1; then
    echo "  ✓ $pkg ($($pkg -version 2>/dev/null | head -1 || $pkg --version 2>/dev/null | head -1))"
  else
    echo "  → brew install $pkg"
    brew install "$pkg"
  fi
done

echo "[2/3] mlx-whisper (Apple GPU STT)"
if command -v mlx_whisper >/dev/null 2>&1; then
  echo "  ✓ mlx_whisper already installed"
elif command -v uv >/dev/null 2>&1; then
  echo "  → uv tool install mlx-whisper (isolated install — recommended)"
  uv tool install mlx-whisper
else
  echo "  → pip install -U mlx-whisper"
  pip install -U mlx-whisper
fi

echo "[3/3] Verify (check by CLI presence)"
fail=0
for c in yt-dlp ffmpeg mlx_whisper; do
  if command -v "$c" >/dev/null 2>&1; then
    echo "  ✓ $c"
  else
    echo "  ✗ $c missing"
    fail=1
  fi
done

if [ "$fail" = 0 ]; then
  echo "Setup complete."
else
  echo "Some tools are missing — check the log above." >&2
  exit 1
fi
