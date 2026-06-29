# Skills

[English](README.md) · [한국어](docs/README_KO.md)

A personal collection of [Agent Skills](https://github.com/vercel-labs/skills) for Claude Code and other compatible AI coding agents. Each skill lives in `skills/<name>/SKILL.md`.

## Installation

Install with the [`skills`](https://github.com/vercel-labs/skills) CLI — no global install needed.

Install everything (choose interactively):

```bash
npx skills add seonggukchoi/skills
```

Or install one or more specific skills with the repeatable `--skill` flag:

```bash
npx skills add seonggukchoi/skills --skill agent-creator --skill youtube-markdown
```

Other commands: `npx skills list`, `npx skills update`, `npx skills remove <skill>`.

## Skills

Each skill can be installed on its own:

| Skill | Description | Install |
| --- | --- | --- |
| [`agent-creator`](skills/agent-creator) | Design, create, diagnose, and improve AI subagent profiles as markdown files. | `npx skills add seonggukchoi/skills --skill agent-creator` |
| [`agent-instruction-management`](skills/agent-instruction-management) | Write, refactor, and manage agent instruction files (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`). | `npx skills add seonggukchoi/skills --skill agent-instruction-management` |
| [`agent-orchestration`](skills/agent-orchestration) | Coordinate, fan out, and synthesize work across multiple subagents. | `npx skills add seonggukchoi/skills --skill agent-orchestration` |
| [`agent-organization-designer`](skills/agent-organization-designer) | Plan and audit an AI agent organization — which agents to have, role boundaries, and scale. | `npx skills add seonggukchoi/skills --skill agent-organization-designer` |
| [`bitwarden-cli`](skills/bitwarden-cli) | Work with passwords, secrets, notes, and Sends through the Bitwarden CLI (VaultWarden / self-hosted / REST). | `npx skills add seonggukchoi/skills --skill bitwarden-cli` |
| [`codex-image-generation`](skills/codex-image-generation) | Generate and edit images via the Codex CLI's built-in `image_gen` (ChatGPT subscription token, no API key). | `npx skills add seonggukchoi/skills --skill codex-image-generation` |
| [`doc-to-markdown`](skills/doc-to-markdown) | Convert document files (PDF, DOCX, PPTX, XLSX, HWP) into clean markdown. | `npx skills add seonggukchoi/skills --skill doc-to-markdown` |
| [`watercrawl`](skills/watercrawl) | Scrape, crawl, and web-search via a self-hosted WaterCrawl API instance (markdown output, JS rendering, screenshots). | `npx skills add seonggukchoi/skills --skill watercrawl` |
| [`youtube-markdown`](skills/youtube-markdown) | Turn YouTube videos into searchable markdown with timestamps and screen captures. | `npx skills add seonggukchoi/skills --skill youtube-markdown` |

Some skills rely on external tools — e.g. the `codex` CLI, the Bitwarden `bw` CLI, `pandoc`, a running WaterCrawl instance (for `watercrawl`), or Apple Silicon + `mlx-whisper` (for `youtube-markdown`). See each skill's `SKILL.md` for its prerequisites.
