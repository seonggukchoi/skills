# Fallback — image_gen.py (OPENAI_API_KEY, fine control, batch)

A Python script bundled with the codex install that provides explicit `generate`/`edit`/`generate-batch` plus fine-grained options like masks and `input-fidelity`. It calls the OpenAI Images API directly, so it **requires an API key and is billed per use**. If Method 1 (built-in image_gen) is enough, don't use this path — use it only in one of the following cases.

- When you need **fine-grained parameter control**, such as mask-based inpainting, transparent backgrounds, or `input-fidelity`.
- When processing a **large batch** of dozens of images or more at once.
- When the user **explicitly** requests using the API key/script.

## Path and setup

```bash
IMG_GEN="$HOME/.codex/skills/.system/imagegen/scripts/image_gen.py"
# The location may vary by version, so search for it if missing
[ -f "$IMG_GEN" ] || IMG_GEN=$(find "$HOME/.codex" -name image_gen.py -path '*imagegen*' 2>/dev/null | head -1)

export OPENAI_API_KEY="sk-..."          # Required (errors without it)
# Dependencies: the openai SDK, plus pillow (when using downscaling/post-processing)
```

Defaults: model `gpt-image-1.5`, size `1024x1024`, quality `auto`, format `png`, output `output/imagegen/output.png`.

## Generate

```bash
python3 "$IMG_GEN" generate --prompt "<prompt>" --out output/img.png
```

## Edit (mask, fine control)

```bash
python3 "$IMG_GEN" edit --image original.png --prompt "<what to change>" --out output/edited.png
```

- Redraw only part (inpainting): `--mask mask.png` — the **transparent (alpha) region** of the mask is redrawn. It must be a PNG with an alpha channel.
- Source detail preservation: `--input-fidelity high` (keep faces, logos, etc.) or `low`.
- Composite/reference multiple inputs: `--image a.png --image b.png` (repeat).

## Batch

```bash
python3 "$IMG_GEN" generate-batch --input jobs.jsonl --out-dir output/ --concurrency 5
```

- `--out-dir` is **required**. One JSONL line = one job. Each line is at minimum `{"prompt": "..."}`.
- Per-line override keys: `out`, `size`, `quality`, `n`, `model`, `background`, `output_format`, etc.

```jsonl
{"prompt": "a red fox in snow", "size": "1536x1024", "out": "fox.png"}
{"prompt": "a blue whale at dawn", "quality": "high"}
```

## Key options (common to generate/edit)

| Option | Value | Notes |
|---|---|---|
| `--size` | `1024x1024` / `1536x1024` / `1024x1536` / `auto` | square / landscape / portrait |
| `--quality` | `low` / `medium` / `high` / `auto` | |
| `--background` | `transparent` / `opaque` / `auto` | transparent only with `png`/`webp` output |
| `--output-format` | `png` / `jpeg` / `webp` | |
| `--n` | `1`–`10` | number of images |
| `--model` | default `gpt-image-1.5` | |
| `--out` / `--out-dir` | path | single file / directory |
| `--no-augment` | (flag) | send the prompt **verbatim** (below) |
| `--dry-run` | (flag) | print only the request payload, no actual call or billing |
| `--force` | (flag) | overwrite an existing output file |

- **`--no-augment`**: the default (augment) prepends `Primary request:` to the prompt and merges in structured hint fields like `--style`, `--scene`, and `--palette`. To send your prompt **as-is**, pass `--no-augment`.
- **`--dry-run`**: useful for verifying that the command is correct and what payload will be sent, even without a key (both edit and generate).
