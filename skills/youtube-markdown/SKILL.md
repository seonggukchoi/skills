---
name: youtube-markdown
description: >-
  Convert what is said and shown in a YouTube video into a readable, searchable markdown
  document with timestamps and screen captures. Given a video URL: secure subtitles →
  (if subtitles are missing or low quality) mlx-whisper STT → for screen-dependent videos,
  ffmpeg frame extraction and multimodal analysis → cross-check subtitles/STT → write up
  and summarize as markdown, then save it under a per-video folder in the current directory
  (cwd) where the agent runs. Use this skill for requests like "summarize this YouTube video",
  "turn this video into a document", "get me a YouTube transcript", "transcribe this
  talk/tutorial into text", "summarize this video into markdown", "transcribe this
  presentation", or whenever a YouTube/youtu.be URL appears alongside an intent to capture
  the video's content as text, a document, or notes. Also use it when an "STT", "subtitle
  extraction", "video summary", or "transcription" request comes with a YouTube link.
  However, this is NOT the skill for — (1) tasks that don't document the content, such as URL
  shortening, thumbnail/video-file downloads, or video editing/clip creation; (2) metadata or
  statistics analysis such as comments, view counts, or subscribers; (3) non-YouTube local
  media files (mp4, m4a, etc.), podcasts, or webpage/blog conversion. Assumes execution on an
  Apple Silicon Mac (mlx-whisper).
---

# YouTube → Markdown

A pipeline for preserving the knowledge in a YouTube video as a **readable, searchable markdown document** rather than as video. The core goal is not plain transcription but a **structured document** (timestamp anchors + screen captures + summary) complete enough that you never have to rewatch the video.

## Execution environment assumption

This skill assumes it runs on an **Apple Silicon Mac (M1/M2/M3/M4)**, because the STT engine is `mlx-whisper`, which uses the Apple GPU (Metal). On Linux/Intel the STT step won't work as-is, so in that case tell the user and discuss alternatives (a transcription API, etc.).

### Setup (one-time)

If the tools are missing, run the setup script — it's idempotent, so it skips anything already present:

```bash
bash scripts/setup.sh
```

It installs and verifies `ffmpeg`/`yt-dlp` (Homebrew) and `mlx-whisper` (isolated install via uv tool). **Caution**: don't check whether mlx-whisper works with `python -c "import mlx_whisper"` — when it's installed into an isolated environment such as uv tool, the import fails under the system python even though the CLI (`mlx_whisper`) works fine. Always verify with `command -v mlx_whisper`.

## Core principles

These three are the backbone of the pipeline. Rather than following the steps mechanically, understand *why* each exists and use judgment.

1. **Subtitles first, STT only when needed.** YouTube's existing subtitles (especially human-authored manual ones) get punctuation and proper nouns right, and they're instant and free. So **always secure subtitles before running STT**. Run STT only when subtitles are absent or their quality is terrible. mlx-whisper may be fast, but running STT when good subtitles already exist is a waste.

2. **mlx-whisper is the only STT engine. No faster-whisper.** On Apple Silicon, `faster-whisper` (CTranslate2) can't use the Metal GPU and runs CPU-only, which is slow. `mlx-whisper` is native to the Apple GPU and is dramatically faster. Use `mlx-community/whisper-large-v3-turbo` as the default model (a balance of accuracy and speed).

3. **Visual analysis only for screen-dependent videos.** Grabbing frames from every video wastes time and context. Speech-centric videos (talks, interviews, podcasts) are fully covered by subtitles/STT alone. Only when the screen carries information (coding tutorials, slide presentations, product demos) do you extract and analyze frames — because the *'this code'* in a subtitle's "paste this code here" exists only on screen.

## Video type branching

In S0, decide the video type and split the path accordingly:

| Type | Subtitles/STT | Frame analysis | Examples |
|---|---|---|---|
| Speech-centric | ✅ | ❌ | Talks, interviews, podcasts |
| Slide presentation | ✅ | ✅ keyframes | Conference talks, lectures |
| Screen demo | ✅ | ✅ required | Coding tutorials, product demos |
| Chart/graph analysis | supplementary | ✅ primary | Data commentary, trading |

If the call is ambiguous, infer from metadata (title, description, category) and the thumbnail; if you're still unsure, ask the user once.

## Workflow

`<VID>` is the video ID that yt-dlp provides. Collect all outputs under **`./<VID>/` in the current working directory (cwd)**. Don't write outside the cwd or to an external store (Obsidian, etc.). **Do not git commit or push** — only when the user explicitly tells you to.

Below, `scripts/...` are paths **relative to this skill's folder** (the "Base directory" in the skill instructions — e.g. `~/.claude/skills/youtube-markdown`). Outputs go to the cwd, scripts come from the skill folder — if this gets confusing, call them by absolute path, like `bash <skill-folder>/scripts/setup.sh`.

### S0 — Metadata & type detection

```bash
yt-dlp -J --no-download "<URL>"     # title/duration/chapters/subtitle tracks/category JSON
```

From this, capture `id` (→ `<VID>`), the title, duration, whether chapters exist, and the list of subtitle tracks, and decide the **video type** (the table above). Then create the output folders:

```bash
mkdir -p "<VID>/work" "<VID>/frames"
```

### S1 — Secure subtitles (first)

```bash
yt-dlp --skip-download --write-subs --write-auto-subs \
  --sub-langs "ko,en" --convert-subs srt \
  -o "<VID>/work/%(id)s.%(ext)s" "<URL>"
```

Subtitle priority: **ko manual > en manual > ko auto > en auto**. If manual subtitles exist, use them as the baseline. If only auto subtitles exist, they need punctuation and misrecognition fixes (handled in the S5 cross-check). If subtitles are sufficient, skip S2 (media download).

### S2 — Media download (conditional)

- Subtitles are sufficient and no screen analysis is needed → **skip download** (the fastest path)
- STT needed → audio only:
  ```bash
  yt-dlp -x --audio-format mp3 -o "<VID>/work/audio.%(ext)s" "<URL>"
  ```
- Screen analysis needed → download the video:
  ```bash
  yt-dlp -f "bestvideo[height<=1080]+bestaudio/best" -o "<VID>/work/video.%(ext)s" "<URL>"
  ```

### S3 — STT (only when subtitles are missing or low quality)

Whisper readily produces **hallucinations** that repeat the same phrase dozens to thousands of times over silent, musical, or applause stretches (especially in Korean, near the end of a video). Turn on the options that *prevent* this from the start:

```bash
mlx_whisper "<VID>/work/audio.mp3" \
  --model mlx-community/whisper-large-v3-turbo \
  --language ko \
  --condition-on-previous-text False \
  --word-timestamps True \
  --hallucination-silence-threshold 2 \
  --initial-prompt "<key proper nouns of the video's topic, comma-separated — e.g.: Assetto Corsa Competizione, camber, damper, MoTeC>" \
  --output-format srt --output-dir "<VID>/work"
```

- `--condition-on-previous-text False`: doesn't condition on the previous output, greatly reducing **repeat-loop hallucinations** (you lose a little contextual consistency, but in long Korean videos repeat hallucinations are the bigger threat).
- `--word-timestamps True --hallucination-silence-threshold 2`: skips a stretch when a hallucination is suspected over silence of 2+ seconds.
- `--initial-prompt`: priming with the video's domain proper nouns reduces misrecognition (pull them from the S0 metadata, title, and description).
- `--language` matches the video's language (Korean `ko`, English `en`; omit it to auto-detect if unknown).

Right after STT, **mechanically cut any repeat hallucinations** that slipped past the prevention, one more time:

```bash
python3 scripts/strip_repeats.py "<VID>/work/audio.srt" -o "<VID>/work/stt.clean.srt" --max-repeat 2 --report
```

For long videos over an hour, run it in the background and poll. **Don't pull the raw STT output into the main context wholesale** — it can run to tens of thousands of tokens. Delegate the cleanup and summarization of long transcripts to a subagent and retrieve only the result.

### S4 — Visual analysis (screen-dependent only)

Extract only scene-change keyframes. Don't extract at N-second intervals — that turns 12 slides into 600. The script **decodes only once** at a low threshold to gather candidates, and if they exceed the target count it keeps only the top by `scene_score` (no need to hand-tune the threshold up and down):

```bash
bash scripts/extract_keyframes.sh "<VID>/work/video.mp4" "<VID>/frames" 40
#                                   video            output          max frames
```

`<VID>/frames/frames.tsv` lists each frame's `pts_time`, `[mm:ss]`, and `scene_score` in chronological order — use them directly as timestamp anchors when writing the document. **View the extracted frames directly with Read** (this is the skill's key strength) and transcribe the slide text, code, and diagrams into prose. If there are dozens of frames or more, distribute them across subagents and retrieve only the captions.

### S5 — Cross-check

If both subtitles and STT exist, compare them and adopt whichever is more accurate.

- **Proper nouns, numbers, technical terms, code identifiers**: decide which side is right (e.g., auto-subtitle "Koo-ber-net-ees" → "Kubernetes", version/figure errors). For a proper noun that recurs throughout a video, **settle on one spelling and use it consistently** across the whole document (e.g., "Assetto Corsa Competizione", "camber", "damper").
- **Removing residual hallucinations**: also look for hallucinations that `strip_repeats.py` missed. **Signals** — (1) the same phrase three or more times in a row; (2) plausible sentences that appear suddenly over silence/BGM/ending stretches ("Thanks for watching" and the like); (3) stretches present only in the STT but not in the subtitles. Aligning the timeline against the subtitles exposes STT-only hallucinations.
- **Restoring punctuation**: auto subtitles have no punctuation, so restore it from the STT or context.

Korean videos vary widely in auto-subtitle quality, so verify especially carefully.

### S6 — Documentation

Write the final document to `./<VID>/<safe-title>.md`. Use **plain, portable markdown only** (no Obsidian wikilinks — this document is kept standalone in the cwd). Structure:

```markdown
# <video title>

> Source: <URL> · Channel: <channel> · Duration: <duration> · Created: <today>

## TL;DR
- (3-line summary)

## Key points
- ...

## Body
### [00:00] <chapter/section title>
Content... embed screen captures with relative paths:
![slide description](frames/0003.jpg)

```code``` — reconstruct from the screen into code blocks.

<details><summary>Full transcript</summary>

(original text with timestamps)

</details>
```

- If chapters exist, make each chapter a section; otherwise, split sections at content transitions.
- Put an `[mm:ss]` timestamp anchor at the head of each section so it can be cross-referenced against the video.
- Embed screen captures with relative paths under `frames/` so the document and images travel together.

### S7 — Summary

Fill in the TL;DR (3 lines) at the top of the document plus the key-point bullets. For a tutorial, add the steps/code to follow along; where applicable, add action items. For long videos, summarize per chapter and then merge into an overall TL;DR (map-reduce).

### S8 — Verify output

Confirm all outputs are under `./<VID>/` in the cwd and report the final path to the user. **Do not perform any git operations.**

```
./<VID>/
├─ <safe-title>.md   ← final document
├─ frames/           ← keyframes + frames.tsv (frame↔timestamp mapping)
└─ work/             ← intermediates: audio, subtitles, STT srt, stt.clean.srt, etc. (user cleans up if needed)
```

## Progress gate

So the user can confirm the direction before the costly steps (STT, frame extraction), **run only S0–S1 first, report the "video type + subtitle status", and then get confirmation on whether to run S4 (frame extraction)**. This avoids wasting STT and frame work on a video that subtitles alone can finish. If the user says "just take it all the way", proceed through the whole pipeline without the gate.

## Caveats

- **Copyright/ToS**: limit downloads to personal study and fair use. Membership/private videos require auth cookies.
- **Korean STT and hallucinations**: Whisper is less accurate in Korean than in English and readily produces repeat hallucinations over silence/BGM stretches → the more Korean the video, the more you layer (1) subtitles first, (2) the S3 hallucination-suppression options, (3) `strip_repeats.py`, and (4) the cross-check.
- **Protecting context**: keep raw STT and large numbers of frames on disk (`work/`, `frames/`) and bring only results into the main context. Isolate heavy processing in subagents.
- **Long videos**: for 3+ hours, split the audio, run STT on the parts, and stitch the timestamps back together.
