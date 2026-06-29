# Per-Agent File Paths and Sync Strategy

Summarizes each agent's global/workspace instruction-file paths, how to set up `@` references, and how to identify active agents.

---

## Per-Agent File Paths

| Agent           | Global Instructions            | Workspace Instruction File       | `@` Reference Support |
| --------------- | ------------------------------ | -------------------------------- | --------------------- |
| **Claude Code** | `~/.claude/CLAUDE.md`          | `CLAUDE.md`                      | O                     |
| **OpenCode**    | `~/.config/opencode/AGENTS.md` | `AGENTS.md`                      | O                     |
| **Codex**       | `~/.codex/instructions.md`     | `AGENTS.md`                      | X                     |
| **Cursor**      | `~/.cursor/rules/`             | `.cursorrules`, `.cursor/rules/` | O (partial)           |
| **Gemini**      | `~/.gemini/GEMINI.md`          | `GEMINI.md`, `.gemini/GEMINI.md` | X                     |

> When an agent is added, update this table first.

### Symlinked Dotfiles (optional pattern)

If you manage your dotfiles with a tool like `lnk`, `stow`, or `chezmoi`, your real instruction file may live inside your dotfiles repo and be symlinked into the standard location. The standard file may in turn `@`-reference an `AGENTS.md` kept alongside it as the single source of truth:

```
~/.claude/CLAUDE.md → <dotfiles-repo>/.claude/CLAUDE.md (content: @./AGENTS.md)
                      <dotfiles-repo>/.claude/AGENTS.md  ← real instruction file
```

**When a standard path is a symlink, resolve it and edit the real file** (e.g., the copy inside your dotfiles repo) so the change survives a re-sync. If you do not use such a tool, edit the standard path (e.g., `~/.claude/CLAUDE.md`) directly.

---

## How to Set Up `@` References

### Agents That Support `@` References (Claude Code, OpenCode)

Put only a single `@`-reference line in that agent's workspace instruction file:

```markdown
@./AGENTS.md
```

**Why use `@` references instead of symlinks**: symlinks can break depending on OS/Git settings (Windows, differences in Git clone config). `@` references are handled at the agent-tool level, so they work reliably regardless of environment.

**Notes**:
- An `@`-reference file contains only the one reference line. Adding other content mixes the reference with standalone content, creating confusion over which takes precedence.
- Do not put a comment or title at the top of the file. The single line `@./AGENTS.md` must be the entire file.

### Agents Without `@` Reference Support

#### Codex
- Reads `AGENTS.md` directly, so no separate file is needed.

#### Gemini
- Needs a dedicated file (`GEMINI.md`). — Gemini does not support `@` references, so it cannot read the source file directly.
- Maintain it by copying the content of `AGENTS.md`.
- When `AGENTS.md` changes, **manually sync** `GEMINI.md` too.
- State the sync source at the top of the file:

```markdown
<!-- This file is synced from AGENTS.md. Do not edit it directly. -->
```

#### Cursor
- Uses `.cursorrules` or the `.cursor/rules/` directory.
- `@` references are partially supported, but for stability prefer including the content directly. — Cursor's `@` reference support is unstable across versions.

---

## Managing Global Instructions

Because each agent has a **different config path**, manage global instructions independently for each.

- Write each agent's global instruction file to suit that agent.
- Even for shared rules, do not consolidate via `@` references at the global level. — Each agent has a different global path, and each parses its global instructions differently.
- When a global rule changes, update **the global instructions of every agent in use**.

### What Goes in Global Instructions

- Include only rules that must **always** apply, regardless of project.
- Examples: response-language setting, communication style, common tool-usage principles, baseline agent behavior principles
- **Strictly prohibited**: specific build commands, per-project Git scope, framework-dependent rules — such rules in global cause confusion in projects that do not use that framework.

### Agent-Specific Rules

Put rules that apply to only one agent in that agent's global instructions:

| Example Rule                | Where to Put It                                | Reason                                          |
| --------------------------- | ---------------------------------------------- | ----------------------------------------------- |
| `mcp__` tool-call conventions | `~/.claude/CLAUDE.md`                        | Only Claude Code supports MCP tools             |
| Using OpenCode subagents    | `~/.config/opencode/AGENTS.md`                 | Only OpenCode provides the subagent feature     |
| Cursor rule-file structure  | `~/.cursor/rules/`                             | Because it concerns Cursor's own rule-file structure |

---

## Identifying Active Agents

Before editing instructions, check **which agents are active** in the current environment. Editing an inactive agent's files is wasted work; missing an active one causes cross-agent inconsistency.

### Identify by Global Instruction File

Check whether each agent's global instruction file exists:

| Agent       | Global Instruction File        |
| ----------- | ------------------------------ |
| Claude Code | `~/.claude/CLAUDE.md`          |
| OpenCode    | `~/.config/opencode/AGENTS.md` |
| Codex       | `~/.codex/instructions.md`     |
| Cursor      | `~/.cursor/rules/`             |
| Gemini      | `~/.gemini/GEMINI.md`          |

### Identify by Workspace Instruction File

Check whether the following files exist at the project root:

- `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, `GEMINI.md`

### Principles

- When editing, update **only the active agents' files**. — Touching files for agents that are not installed creates unnecessary files and can cause confusion.
- Do not touch files for agents that are not installed.
- If a new instruction file must be created, create it only for active agents.
