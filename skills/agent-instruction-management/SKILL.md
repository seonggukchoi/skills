---
name: agent-instruction-management
description: Use when the user asks to 'edit CLAUDE.md', 'add to AGENTS.md',
  'update the instructions', 'add a rule', 'change the agent guidelines',
  'add a rule to prevent this mistake', 'clean up the instructions',
  'refactor the instructions', 'consolidate duplicate rules',
  'update agent instructions', 'add a rule', 'refactor instructions',
  'sync the agent config', 'create an instruction file',
  'promote this rule to global', 'add an agent rule',
  'put this in the instruction file', 'add this rule to CLAUDE.md',
  'show the instruction-file status', 'register this pattern as a rule',
  'check the workspace instructions', 'tidy up the agent config files',
  'apply this to the global config', or for any task involving writing,
  editing, refactoring, or managing agent instruction files (CLAUDE.md,
  AGENTS.md, GEMINI.md, etc.), or when the agent spots a recurring mistake
  pattern during work and judges that instructions need to be
  added/changed/improved. Even if the user does not explicitly use the words
  'instructions' or 'rule', use this skill whenever there is intent to define
  or change an AI agent's behavioral rules.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(ls *), Bash(cat *)
---

# Agent Instruction Authoring/Editing Guide

Defines the procedures for authoring, editing, refactoring, and managing the instruction files that specify the behavioral rules of AI coding agents. **Supports multiple agents at once**, following a strategy that keeps `AGENTS.md` as the Single Source of Truth.

---

## Core Principle: Context Efficiency (Top Priority)

Because instruction files are loaded on every request, **minimizing context is the default for all work**. When adding, editing, refactoring, or reviewing, always apply the following while preserving meaning:

- **Prefer terse phrasing**: reduce full sentences to noun phrases, fragments, or imperatives; drop filler verb endings
- **Remove unnecessary dividers**: keep `---` only where essential, e.g., long section boundaries
- **Merge similar items**: when 3+ bullets share the same context, consider collapsing them into one inline line or a single sentence
- **Avoid over-emphasis**: use "always"/"never" only where it truly matters
- **Remove decorative modifiers**: cut repetitive explanation and rhetorical phrasing

> When no meaning is lost, always go shorter. Verbose instructions waste tokens and scatter the agent's attention.

---

## Instruction File System

### File Paths by Agent (Summary)

| Agent           | Workspace Instructions | `@` Reference Support |
| --------------- | ---------------------- | --------------------- |
| **Claude Code** | `CLAUDE.md`            | O                     |
| **OpenCode**    | `AGENTS.md`            | O                     |
| **Codex**       | `AGENTS.md`            | X                     |
| **Cursor**      | `.cursorrules`         | O (partial)           |
| **Gemini**      | `GEMINI.md`            | X                     |

> For details such as global instruction paths and sync strategy, see [agent-file-paths.md](references/agent-file-paths.md).

### Hierarchy and Priority

| Layer         | Scope         | Examples                                                      |
| ------------- | ------------- | ------------------------------------------------------------ |
| **Global**    | All projects  | Response language, communication style, common tool-usage principles |
| **Workspace** | Current project | Build commands, Git scope, code style, testing method      |

- **Priority**: Workspace > Global (the specific overrides the general)

### Source File Rules

- **Workspace**: `AGENTS.md` is the **only source**.
  - Agents that support `@` references: the instruction file contains only the single line `@./AGENTS.md`.
  - Agents without `@` reference support: read `AGENTS.md` directly, or maintain a synced copy.
- **Global**: since each agent has a different config path, **manage each independently**.
- When editing, **edit only `AGENTS.md`** and the `@`-reference files update automatically.

> For how to set up `@` references and the sync strategy for unsupported agents, see [agent-file-paths.md](references/agent-file-paths.md).

---

## Deciding: Global vs. Workspace

Decide **where** to put an instruction using these criteria:

| Decision Question                           | Global | Workspace |
| ------------------------------------------- | :----: | :-------: |
| Does it always apply, regardless of project? |   O    |           |
| Does it depend on a specific tech stack?    |        |     O     |
| Does it depend on a specific build/test tool? |       |     O     |

**When in doubt**: put it in the workspace first. A wrong placement in global applies an unnecessary rule to every project, with large side effects; a workspace placement is limited to that one project, so the risk is small. Once it recurs across several projects, propose promoting it to global.

---

## Edit Classification Criteria

### Minor Edits (auto-apply → report afterward)

Must satisfy **all** of the following:

1. The rule's **meaning does not change**
2. **No new rule** is added
3. **No existing rule** is deleted or weakened
4. It is a **factual correction**

Applies to: typos, broken links, command/path updates, Markdown syntax errors, meaning-preserving compression (style tightening, divider cleanup, removing redundant wording)

### Significant Edits (require prior approval)

| Situation                                        | Action                                            |
| ------------------------------------------------ | ------------------------------------------------- |
| Recurring mistake pattern found during work      | Propose adding a rule to the user → edit after approval |
| Mismatch found between existing instructions and actual code | Report to the user → edit after approval |
| User explicitly requests an edit                 | Confirm the content, then edit immediately        |
| New important pattern/rule discovered            | Propose to the user → edit after approval         |
| Deleting or weakening an existing rule           | **Always** requires an explicit user request      |
| Refactoring (dedup, structure improvement, etc.) | Propose a change plan to the user → edit after approval |

---

## Edit Procedure

### Step 1. Analyze

Understanding the current state accurately prevents putting a rule in the wrong place or conflicting with existing rules.

1. Identify the **reason** the edit is needed.
2. Decide the target file: global vs. workspace.
3. Read the relevant sections of the existing instructions to check for **conflicts/duplication**.
4. **Identify the active agents** to finalize the list of files to update.
   - For how to identify them, see the "Identifying Active Agents" section of [agent-file-paths.md](references/agent-file-paths.md).

### Step 2. Classify

Because the approval process differs by edit scope, distinguishing minor vs. significant first prevents unnecessary approval delays or unauthorized changes.

- **Minor edit** → Step 3-A
- **Significant edit** → Step 3-B

### Step 3-A. Minor Edit

Since the meaning does not change, handle it quickly and report afterward.

1. Edit the `AGENTS.md` source (or the global instructions)
2. Verify the `@`-reference files are intact
3. Also update the synced files of agents without `@` support
4. **Report the edit afterward** to the user (briefly explain what was changed and why)

### Step 3-B. Significant Edit

Since the rule's meaning changes or a new rule is added, get prior approval so the user can confirm the intent.

1. Present an **edit proposal** to the user:
   - Reason for the edit
   - Files to edit (global/workspace, which agents)
   - Preview of the changes
2. Execute after user **approval**
3. Edit `AGENTS.md` → verify `@` references → update synced files

### Step 4. Verify

Check file state after editing to catch broken references or cross-agent contradictions early.

- Verify Markdown syntax validity
- Verify each `@`-reference file contains only one line
- Verify there is no contradiction between global and workspace
- For global edits: verify the change is reflected in every active agent's global instructions

---

## Instruction Authoring Rules

### Document Structure

- **Heading scheme**: `##` for major sections, `###` for subsections (follow the existing document's scheme)
- New sections: place them where they fit the existing document's logical flow.
- If a relevant section already exists, add the item there instead of creating a new section.

### Writing Tone

- **Imperative/directive voice**: "do X", "do not X", "X prohibited"
- **Prefer terse phrasing**: collapse repetitive full sentences into fragments or imperatives
- Use `**strictly prohibited**` for prohibitions and `**always**` for requirements (do not overuse)
- **Never use** vague wording ("if possible", "preferably")
- Remove decorative modifiers and repetitive explanation

### Agent Compatibility

- Write `AGENTS.md` rules to be **agent-neutral**.
- Put agent-specific features (tool names, command syntax) only in that agent's global instructions.
  - e.g., `mcp__` tool calls → document only in `~/.claude/CLAUDE.md`
  - e.g., OpenCode-only subagent config → document only in `~/.config/opencode/AGENTS.md`

### Content Rules

- **Examples required**: abstract rules **must** include concrete examples (commands, code snippets, file paths). A rule without examples gets interpreted in many ways, hurting consistency.
- **State the reason**: briefly explain why the rule is needed. The agent must understand a rule's intent to apply it correctly.
- **Avoid duplication**: do not repeat in the workspace instructions what is already in the global instructions. Duplication causes drift when only one side is updated.
- **List conventions**: ordered procedure → numbers, parallel items → bullets, comparison/summary → table.

> For concrete good-vs-bad rule comparisons, see [rule-writing-examples.md](examples/rule-writing-examples.md).

---

## Refactoring Instructions

Refactoring improves document quality **while preserving the rules' meaning**. It is classified as a **significant edit** and always requires prior approval.

### Signs Refactoring Is Needed

| Sign                          | Example                                            |
| ----------------------------- | -------------------------------------------------- |
| Same rule in multiple places  | Identical content repeated in global and workspace |
| Related rules scattered       | A Git rule wedged inside the testing section       |
| Verbose, repetitive explanation | The same point restated three times in different words |
| Verbose style / excess dividers | Repetitive full sentences, unnecessary `---`, excessive modifiers |
| Obsolete rules                | A rule for a removed tool still lingers            |
| Cross-agent inconsistency     | Claude Code and OpenCode global rules mean different things |

### Core Refactoring Principles

- **Compression by default**: make the core principle (context efficiency) the baseline goal of every refactor.
- **Preserve meaning**: even when compressing, keep the key directives and examples.
- **Prevent information loss**: when removing duplicates, merge the unique information from each version.
- **Apply incrementally**: roll out in stages by type (dedup → structure → compression).
- **Beware obsolete rules**: even if it no longer matches the current code, it may carry future intent. Confirm with the user before deleting.

> For detailed per-type procedures, see [refactoring-guide.md](references/refactoring-guide.md).

---

## Migrating the Sync Structure

If you find per-agent instruction files set up as **duplicate files** or **symbolic links**, migrate them to the standard structure: an `AGENTS.md` source plus `@` references.

- Migration is classified as a **significant edit** and requires user approval.
- Before migrating, check the current structure first to avoid losing existing file content.
- **Do not apply this migration at the global level.** Global instructions are managed independently per agent.

> For the detailed migration procedure, see [sync-migration.md](references/sync-migration.md).

---

## Prohibitions

- Do not **delete or weaken** an existing rule without an explicit user request. — Arbitrarily changing a rule the user added on purpose erodes trust.
- Do not include **executable code, secrets (API keys, tokens), or environment variable values** in instruction files. — Instruction files are version-controlled, so secrets risk exposure.
- Do not put **project-specific content in global instructions**. — It applies unnecessary rules in other projects and causes side effects.
- Do not put **globally applicable content in workspace instructions**. — You end up rewriting the same rule per project, making maintenance hard.
- Do not edit `@`-reference files directly instead of `AGENTS.md`. — The source and the reference drift apart, so different agents follow different rules.
- Do not auto-apply changes beyond the scope of a minor edit. — If an important rule changes without the user's knowledge, debugging is extremely hard.
- **Do not create instruction files for agents that are not installed.** — Unused files clutter the project and cause confusion.

---

## Updating This Skill Itself

This skill is a **living document**. Update it alongside the following changes:

- Adding/removing a supported agent → update the file-path table + [agent-file-paths.md](references/agent-file-paths.md)
- Change to the instruction-file system → update the relevant sections
- Change to the minor/significant criteria → update the Edit Classification Criteria section
- Change to the sync method → update [sync-migration.md](references/sync-migration.md)

---

## References

### Reference Files
- [agent-file-paths.md](references/agent-file-paths.md) -- per-agent global/workspace paths, `@` reference setup, how to identify active agents
- [sync-migration.md](references/sync-migration.md) -- migration from duplicate-file/symlink setups to the standard structure
- [refactoring-guide.md](references/refactoring-guide.md) -- detailed per-type refactoring procedures and how to audit

### Example Files
- [rule-writing-examples.md](examples/rule-writing-examples.md) -- good-vs-bad rule comparisons and rule-writing examples across domains
