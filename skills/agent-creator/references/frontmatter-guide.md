# Agent Frontmatter Field Guide

A reference for the YAML frontmatter fields at the top of an agent markdown file. **Claude Code and OpenCode use different frontmatter formats.** Before creating a new agent, always check the actual format of an existing agent file and follow the same format.

```bash
# Check existing agent format
head -40 ~/.claude/agents/*.md 2>/dev/null
head -40 ~/.config/opencode/agents/*.md 2>/dev/null
```

---

## Formats by Environment

### Claude Code (`~/.claude/agents/*.md`)

| Field         | Required     | Type   | Description                                                  |
| ------------- | ------------ | ------ | ------------------------------------------------------------ |
| `name`        | **Required** | string | kebab-case name identical to the filename                    |
| `description` | **Required** | string | role description + `<example>` blocks (used for the main session's agent selection) |
| `model`       | **Required** | string | fixed to `inherit`. Inherits the main session's model        |
| `color`       | Recommended  | string | terminal display color (`red`, `green`, `blue`, `yellow`, `cyan`, `magenta`, `white`) |
| `tools`       | **Required** | array  | array of available tools (e.g., `["Read", "Write", "Edit", "Bash", "Glob", "Grep"]`) |

### OpenCode (`~/.config/opencode/agents/*.md`)

| Field         | Required     | Type   | Default       | Description                                     |
| ------------- | ------------ | ------ | ------------- | ----------------------------------------------- |
| `description` | **Required** | string | None          | describes the agent's role and core responsibilities in 1-2 sentences |
| `mode`        | **Required** | string | None          | agent execution mode. Use `subagent`            |
| `temperature` | Recommended  | number | Model default | controls output creativity/consistency (0.0-1.0) |
| `tools`       | Recommended  | object | None          | per-tool true/false setting                     |
| `permission`  | Recommended  | object | None          | per-tool permission-level setting               |

---

## Shared Principles

- **Don't set a different model per agent** — it makes cost hard to predict and breaks output-quality consistency. In Claude Code use `model: inherit`; in OpenCode, omit the model field to inherit the main session's model.
- **Least-privilege principle**: enable only the tools the role needs — enabling unnecessary tools lets the agent perform unintended actions.
- **Keep the format consistent with existing agents** — mixing formats within the same environment makes management hard.

---

## Field Details

### description

Describes the agent's role and core responsibilities. It is the basis for agent selection.

**Writing rules:**
- Use concrete action verbs: "analyzes", "generates", "validates"
- Use concrete action verbs instead of vague expressions: "analyzes", "generates" instead of "helps"

**Claude Code — include `<example>` blocks (required):**

The main session references the `<example>` blocks when auto-selecting an agent. Include three examples to specify the representative situations the agent handles.

```yaml
description: |
  Senior tech lead. Proactively identifies technical risks 3-6 months out and validates architecture/tech-stack choices.

  <example>
  Context: The architecture for a new feature must be decided
  user: "Review the architecture"
  assistant: "I'll analyze the current codebase and requirements to review the architecture's suitability and provide guidance"
  <commentary>
  Architecture validation is a core responsibility of the senior tech lead.
  </commentary>
  </example>
```

**OpenCode — 1-2 sentences:**

```yaml
description: Senior tech lead. Proactively identifies technical risks 3-6 months out, validates architecture/tech-stack choices, and guards against both over-engineering and under-engineering.
```

**Bad example:**
```yaml
description: An agent that provides technical help
```

### name (Claude Code only)

A kebab-case name identical to the filename.

```yaml
name: senior-tech-lead
```

### model (Claude Code only)

Fixed to `inherit`. Inherits the main session's model.

```yaml
model: inherit
```

### color (Claude Code only)

A color that visually distinguishes the agent in the terminal. Choose one that doesn't clash with existing agents, though clashing doesn't affect behavior.

```yaml
color: yellow
```

Available colors: `red`, `green`, `blue`, `yellow`, `cyan`, `magenta`, `white`

### mode (OpenCode only)

Specifies the agent's execution mode. Currently only `subagent` is used.

```yaml
mode: subagent
```

### temperature (OpenCode only)

Controls the creativity and consistency of the output.

**Recommended values by role:**

| Role type                            | Recommended temperature | Reason                       |
| ------------------------------------ | ----------------------- | ---------------------------- |
| Analysis/validation (tech lead, QA, DBA) | 0.1-0.2             | consistency and accuracy matter |
| Strategy/planning (PM, CEO support)  | 0.3-0.4                 | structured thinking + some flexibility |
| Creative/marketing (copywriter, marketer) | 0.5-0.7            | needs to generate diverse ideas |
| Customer-facing (CS)                 | 0.3-0.4                 | empathy + consistent tone    |
| Operations (DevOps, security)        | 0.1-0.2                 | accuracy and safety come first |

### tools

Configures the tools the agent can use.

**Available tools:**

| Tool          | Description         | Side effect        |
| ------------- | ------------------- | ------------------ |
| Read / read   | Read files          | None               |
| Write / write | Write files         | Yes                |
| Edit / edit   | Modify files        | Yes                |
| Glob / glob   | File pattern search | None               |
| Grep / grep   | File content search | None               |
| Bash / bash   | Run shell commands  | Yes (depends on command) |

**Claude Code — array format:**

```yaml
# Full-access role
tools: ["Read", "Write", "Edit", "Bash", "Glob", "Grep"]

# Read-only role
tools: ["Read", "Glob", "Grep"]

# File-creating role (no Bash)
tools: ["Read", "Write", "Edit", "Glob", "Grep"]
```

**OpenCode — object format:**

```yaml
# Full-access role
tools:
  read: true
  write: true
  edit: true
  glob: true
  grep: true
  bash: true

# Read-only role
tools:
  read: true
  glob: true
  grep: true
  write: false
  edit: false
  bash: false
```

### permission (OpenCode only)

Sets fine-grained per-tool permissions. Choose among `allow` (auto-allow), `ask` (confirm each time), and `deny` (block).

**Structure:**
```yaml
permission:
  {tool name}: {permission}
```

**Pattern matching (bash tool):**
```yaml
permission:
  bash:
    "*": ask                    # Default: confirm every command
    "git log*": allow           # git log auto-allowed
    "git diff*": allow          # git diff auto-allowed
    "rm -rf*": deny             # rm -rf blocked
```

**Recommended settings by role:**

```yaml
# Conservative (most roles)
permission:
  edit: ask
  bash:
    "*": ask

# Allow read-only commands only
permission:
  bash:
    "*": ask
    "git log*": allow
    "git diff*": allow
    "git status*": allow

# Allow file edits, restrict bash
permission:
  edit: allow
  bash:
    "*": deny
```

---

## Full Combination Examples

### Claude Code — Senior Tech Lead

```yaml
---
name: senior-tech-lead
description: |
  Senior tech lead. Proactively identifies technical risks and validates architecture choices.

  <example>
  Context: The architecture for a new feature must be decided
  user: "Review the architecture"
  assistant: "I'll analyze the current codebase and requirements to review its suitability"
  <commentary>
  Architecture validation is a core responsibility of the senior tech lead.
  </commentary>
  </example>
model: inherit
color: yellow
tools: ["Read", "Write", "Edit", "Bash", "Glob", "Grep"]
---
```

### Claude Code — Customer Support

```yaml
---
name: customer-support
description: |
  Customer support agent. Handles customer messages as a first line of response to protect the operator's time and sanity.

  <example>
  Context: A customer has asked how to use the service
  user: "Answer the customer inquiry"
  assistant: "I'll classify the customer inquiry and draft a response based on the FAQ"
  <commentary>
  Handling customer inquiries is the CS agent's core job, so call it immediately.
  </commentary>
  </example>
model: inherit
color: cyan
tools: ["Read", "Write", "Edit", "Glob", "Grep"]
---
```

### OpenCode — Senior Tech Lead

```yaml
---
description: Senior tech lead. Proactively identifies technical risks and validates architecture choices.
mode: subagent
temperature: 0.2
tools:
  write: true
  edit: true
  bash: true
  read: true
  glob: true
  grep: true
permission:
  edit: ask
  bash:
    "*": ask
    "git log*": allow
    "git diff*": allow
    "git status*": allow
---
```

### OpenCode — Customer Support

```yaml
---
description: Customer support. Analyzes customer inquiries, drafts responses, and derives product improvements from recurring inquiry patterns.
mode: subagent
temperature: 0.4
tools:
  read: true
  write: true
  edit: true
  glob: true
  grep: true
  bash: false
permission:
  edit: ask
---
```

---

## Caveats

1. **Always check existing agent format**: before creating a new agent, read at least one existing agent file from the same environment to confirm the actual format.
2. **Don't mix formats across environments**: don't mix the Claude Code format and the OpenCode format within the same directory.
3. **Consistency between tools and permission** (OpenCode): setting a permission for a tool you set to `false` in tools is meaningless.
4. **Be careful with bash permissions**: bash is the most powerful tool. `allow` only the command patterns you need and set the rest to `ask`.
5. **description length**: in Claude Code it gets long because of the `<example>` blocks, but keep the first 1-2 sentences of the role description concise. For OpenCode, 2 sentences or fewer is recommended.
