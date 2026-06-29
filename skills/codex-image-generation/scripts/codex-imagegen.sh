#!/usr/bin/env bash
# Generate/edit images with codex's built-in image_gen (uses the ChatGPT subscription token, no OpenAI API key needed).
#
# Usage:
#   codex-imagegen.sh gen  "<prompt>" <out.png>
#   codex-imagegen.sh edit <src.png> "<change>" <out.png> [<extra-src.png> ...]
#
# Saves the result to the given <out.png> (both absolute and relative paths allowed) and prints its absolute path to stdout.
# If codex fails to copy the result to the target path, it falls back to retrieving the latest file from ~/.codex/generated_images.
#
# Note: the default behavior relies on codex copying the result file into the workspace. In environments where
#       the codex sandbox is restricted to workspace-write, <out.png> must be in a writable location (e.g., under the current directory).
set -euo pipefail

die() { printf 'codex-imagegen: %s\n' "$*" >&2; exit 1; }

abspath() { case "$1" in /*) printf '%s\n' "$1" ;; *) printf '%s\n' "$PWD/$1" ;; esac; }

# codex may be installed via mise/nvm, etc. and absent from the non-login shell PATH. Search for it step by step.
resolve_codex() {
  if command -v codex >/dev/null 2>&1; then command -v codex; return 0; fi
  local p
  p=$(zsh -lc 'command -v codex' 2>/dev/null || true)
  if [ -n "$p" ]; then printf '%s\n' "$p"; return 0; fi
  p=$(find "$HOME/.local/share/mise/installs/node" -maxdepth 3 -name codex -type f 2>/dev/null | head -1 || true)
  if [ -n "$p" ]; then printf '%s\n' "$p"; return 0; fi
  return 1
}

# If the expected output path has no file, copy the latest one from generated_images to retrieve it (assumes sequential execution).
recover_output() {
  local out="$1"
  [ -f "$out" ] && { printf '%s\n' "$out"; return 0; }
  local latest
  latest=$(ls -t "$HOME/.codex/generated_images"/*/ig_*.png 2>/dev/null | head -1 || true)
  if [ -n "$latest" ] && cp "$latest" "$out" 2>/dev/null && [ -f "$out" ]; then
    printf '%s\n' "$out"; return 0
  fi
  die "Failed to produce the result file: $out  (check 'codex login status' and 'codex features list | grep image_generation')"
}

# Uses the global PROMPT, OUT_ABS, CODEX. Takes codex exec options (e.g., -i) as arguments.
run_image_gen() {
  mkdir -p "$(dirname "$OUT_ABS")"
  "$CODEX" exec --full-auto --skip-git-repo-check "$@" "$PROMPT" >/dev/null 2>&1 \
    || die "codex execution failed (check login/network/feature enablement)"
  recover_output "$OUT_ABS"
}

cmd_gen() {
  [ $# -ge 2 ] || die 'usage: gen "<prompt>" <out.png>'
  local prompt="$1"
  OUT_ABS=$(abspath "$2")
  PROMPT="Use your built-in image_gen tool to generate exactly one image. ${prompt}. \
After saving, copy the result to the absolute path ${OUT_ABS} and then print ${OUT_ABS} on its own line."
  run_image_gen
}

cmd_edit() {
  [ $# -ge 3 ] || die 'usage: edit <src.png> "<change>" <out.png> [<extra-src.png> ...]'
  local src="$1" change="$2"
  OUT_ABS=$(abspath "$3")
  shift 3
  [ -f "$src" ] || die "source image not found: $src"
  local -a imgs=(-i "$src")
  local extra
  for extra in "$@"; do
    [ -f "$extra" ] || die "extra input image not found: $extra"
    imgs+=(-i "$extra")
  done
  PROMPT="Use your built-in image_gen tool to edit the attached image. Change: ${change}. \
Keep everything else unchanged. \
After saving, copy the result to the absolute path ${OUT_ABS} and then print ${OUT_ABS} on its own line."
  run_image_gen "${imgs[@]}"
}

main() {
  local cmd="${1:-}"
  [ -n "$cmd" ] || die 'usage: codex-imagegen.sh gen|edit ...'
  shift
  CODEX=$(resolve_codex) \
    || die "codex CLI not found. After installing, verify ChatGPT login with 'codex login status'."
  # Put codex's runtime directory (node, etc.) at the front of PATH so it runs even in a non-login shell.
  PATH="$(dirname "$CODEX"):$PATH"; export PATH
  case "$cmd" in
    gen)  cmd_gen  "$@" ;;
    edit) cmd_edit "$@" ;;
    *)    die "unknown command: $cmd (gen|edit)" ;;
  esac
}

main "$@"
