---
name: codex-image-generation
description: >-
  How to generate and edit images with the Codex CLI's (`codex`) built-in image_gen tool. Prefers the
  built-in image_gen (`codex exec`, no OpenAI API key needed) that runs on a ChatGPT subscription token as
  Method 1, and a fallback script (gpt-image-1.5) that requires OPENAI_API_KEY as Method 2. Use for any
  request to create or fix images through codex: "generate/make an image with codex", "draw a
  picture/illustration with codex", "codex image_gen", "create a PNG with codex exec", "edit/modify this
  image with codex", as well as codex-based inpainting, mask editing, compositing multiple images, and batch
  image generation. Trigger proactively for image work in a codex/Codex CLI context even when the user does
  not say "image_gen" explicitly. Do not use for image generation unrelated to codex (Midjourney, the DALL·E
  web app, other tools), or when only a simple resize or format conversion is needed.
---

# Codex image generation and editing

How to create and fix images with the Codex CLI (`codex`). There are two paths, and you **always use Method 1 first**.

| | Method 1: built-in image_gen | Method 2: fallback script |
|---|---|---|
| Invocation | `codex exec` (or the bundled helper) | run `image_gen.py` directly |
| Auth | **ChatGPT login** (no API key) | requires `OPENAI_API_KEY` |
| Billing | **counts toward ChatGPT subscription usage** | OpenAI API pay-per-use (extra cost) |
| Editing | ✅ attach the source with `-i` | ✅ mask, input-fidelity |
| Batch | repeated calls | ✅ `generate-batch` |

**Method 1 (ChatGPT subscription token) is the default.** Do Method 1 first, whether generating or editing. Use Method 2 (pay-per-use API key) only when you need fine control such as mask inpainting, transparent backgrounds, or large batches, or when the user explicitly requests it → [references/fallback-script.md](references/fallback-script.md).

## Pre-checks

```bash
codex login status                              # "Logged in using ChatGPT" means Method 1 is available
codex features list | grep image_generation     # "stable ... true" means image_gen is usable
```

If you get `codex: command not found`, the PATH is missing in a non-interactive shell (common when installed via mise/nvm, etc.). Find the real path with `whence -p codex` (zsh) in a login shell and call it by absolute path. The bundled helper below handles this lookup automatically.

---

## Method 1 — built-in image_gen (default)

### Simplest approach: the bundled helper

This skill's `scripts/codex-imagegen.sh` handles "resolve the codex path → assemble `codex exec` → retrieve the result to the target path" in one step. It prints the result's absolute path to stdout.

```bash
# Generate:  gen "<English prompt>" <out.png>
bash scripts/codex-imagegen.sh gen "a single red apple on a plain white background, flat vector, no text" apple.png

# Edit:  edit <source> "<change>" <out.png>   (attach the source with -i)
bash scripts/codex-imagegen.sh edit apple.png "make the apple blue instead of red" apple-blue.png

# Composite/reference multiple images: append extra images after the edit arguments
bash scripts/codex-imagegen.sh edit base.png "place the logo top-right" out.png logo.png
```

`<out.png>` accepts both relative and absolute paths, and the helper creates any needed parent directories. If codex fails to copy the result to the target path, it automatically retrieves the latest file from `~/.codex/generated_images`. Specify size, aspect ratio, etc. in natural language in the prompt (e.g., `... wide 3:2 composition. Size 1536x1024.`).

### Direct invocation (without the helper / how it works)

Call the built-in tool with `codex exec`. The key is to instruct it to produce **exactly one image at a time** and to **print the save path**.

```bash
# Generate
codex exec --sandbox workspace-write --skip-git-repo-check \
  "Use your built-in image_gen tool to generate exactly one image. <English prompt>. \
After saving, copy it into the current working directory as out.png and print its absolute path on its own line."

# Edit — attach the source with -i (pass it multiple times for multiple inputs)
# The -- before the prompt is required: -i takes a variadic list and would otherwise eat it.
codex exec --sandbox workspace-write --skip-git-repo-check -i /abs/path/original.png -- \
  "Use your built-in image_gen tool to edit the attached image. \
Change: <change>. Keep everything else unchanged. \
After saving, copy it into the current working directory as edited.png and print its absolute path on its own line."
```

- `--sandbox workspace-write`: lets codex write its result into the working directory without an approval prompt. It replaces the older `--full-auto`, which was deprecated in 0.142.2 and **removed in 0.147.0** — passing it now fails with `error: unexpected argument '--full-auto' found`. Valid values are `read-only`, `workspace-write`, and `danger-full-access`; `read-only` blocks the copy step this skill depends on.
- `--skip-git-repo-check`: runs even outside a git repository
- `-i FILE`: attaches an image. It is declared as `--image <FILE>...` (variadic), so put `--` before the prompt or it is consumed as another filename and codex fails with `No prompt provided via stdin`.
- Redirect stdin from `/dev/null` when scripting. codex appends piped stdin to the prompt, so an open pipe leaves it waiting on `Reading additional input from stdin...` instead of running.

### Getting the result (when invoking directly)

The built-in tool saves each result in a different UUID folder (`~/.codex/generated_images/<UUID>/ig_*.png`). So rather than finding it with a fixed glob, the most robust approach is to **have codex copy it into the working directory and use the path it reports**.

```bash
# 1) Recommended: capture the absolute path printed by the prompt via -o and parse it
codex exec --sandbox workspace-write --skip-git-repo-check -o /tmp/last.txt \
  "Use your built-in image_gen tool to generate exactly one image. <prompt>. \
After saving, copy it into the current working directory as out.png and print its absolute path on its own line."
grep -oE '/[^[:space:]]+\.png' /tmp/last.txt | tail -1

# 2) Find it directly: the original lives under a UUID subfolder (the glob needs */, portable on macOS)
ls -t "$HOME/.codex/generated_images"/*/ig_*.png 2>/dev/null | head -1
```

> Note: the path is `generated_images/<UUID>/ig_*.png`, **not a direct child**. Also, `find ... -printf` is GNU-only and fails with macOS's default `find` (BSD), so use the `ls -t` glob above.

### Tips
- If the tone is off, change prompt elements **one at a time** and regenerate.
- If you need multiple images, **repeating the command** is easier to track than bumping "exactly one" higher.

---

## Method 2 — fallback script (key required, fine control, batch)

A pay-per-use path that requires `OPENAI_API_KEY`. Use it only when you need fine control that Method 1 can't do, such as mask inpainting, transparent backgrounds, `input-fidelity`, or large batches. For command and option details → **[references/fallback-script.md](references/fallback-script.md)**.

```bash
# Summary: generate / edit / generate-batch from image_gen.py bundled with the codex install
python3 "$HOME/.codex/skills/.system/imagegen/scripts/image_gen.py" \
  generate --prompt "<prompt>" --out output/img.png
```

---

## Which method to use
- Quick generation/editing without a key, the default → **Method 1** (the `scripts/codex-imagegen.sh` helper or `codex exec`)
- Mask inpainting, transparent backgrounds, `input-fidelity`, large batches, reproducible parameters → **Method 2** ([references/fallback-script.md](references/fallback-script.md))
- The user explicitly wants the API key/script → **Method 2**
- Otherwise, always try **Method 1** (ChatGPT subscription token) first.
