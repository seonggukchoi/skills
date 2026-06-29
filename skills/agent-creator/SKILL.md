---
name: agent-creator
description: |
  Design and create roles and profiles for new AI agents (subagents) as markdown files, or diagnose, fix, and improve existing agents.

  TRIGGER when: "create an agent", "add a subagent", "generate an agent", "new agent", "define an agent's role", "agent profile", "edit the agent", "improve the agent", "diagnose the agent", "fix the agent", "the agent isn't working", "change the agent's tone", "need to add an agent", "design a subagent", "test the agent", "agent status", or any request to create/modify/delete files under `~/.claude/agents/`, or any request to build an agent for a specific role (e.g. "marketer", "DBA", "DevOps").
  DO NOT TRIGGER when: *invoking* an agent to do work (e.g. "@junior-developer implement this feature"), designing the overall agent-organization structure (→ agent-organization-designer), or editing CLAUDE.md/AGENTS.md instruction files (→ agent-instruction-management).
---

# Creating and Improving AI Agent Profiles

Design AI agents with clear roles and boundaries. You can build a new agent from scratch, or modify and improve an existing one.

When using this skill, your job is to figure out where the user is in this process and then proceed together from the appropriate step. The entry point depends on the user's request:

- "Create a marketer agent" → **new agent creation** workflow
- "Our existing CS agent's tone is too stiff" → **improving an existing agent** workflow
- "Show me the status of our agents" → catalog/diagnosis (see the profile validation section)
- "I need to create three agents" → confirm priorities, then proceed sequentially

Always stay flexible. If the user says "just make it quick," minimize the elaboration steps; if they say "let's design it carefully," cover each section in detail.

---

## Communicating with the User

Agent profile creation can be requested by users of varying technical levels. Pay attention to contextual cues and adjust how you communicate.

- If the user uses terms like "subagent" or "prompt engineering," you can communicate in technical terms
- If the user uses everyday language like "make me one more AI employee," reduce the jargon and guide them naturally
- When unsure, a short explanation is fine (e.g., "frontmatter is the settings block at the top of the file")
- When asking questions, offer choices rather than open-ended questions — this reduces the user's decision-making burden

---

## Core Principles

### Purpose Clarity

Every agent must have a clear reason to exist. If you can't answer "Why is this agent needed?" in a single sentence, the agent is still under-defined.

### Minimize Roles

The fewer agents, the better. As the number of agents grows, management overhead increases, role boundaries blur, and it becomes confusing which agent to call. If two can be merged into one, merge them.

### Clear Boundaries

If responsibilities overlap with another agent, two agents compete over the same request or do duplicate work. Anyone should be able to tell at a glance, "This is that agent's job."

### Save the User's Time

An agent should reduce the user's decision-making burden. If the agent itself becomes a management burden, the whole point is lost.

---

## Creating a New Agent

### Step 1. Survey Existing Agents

Check for existing agent files in these locations:

- Global: `~/.claude/agents/` and `~/.config/opencode/agents/`
- Project: `.claude/agents/` and `.opencode/agents/`

Read each agent's description to map out the list of roles. Why this step matters: if you create a role that overlaps with an existing agent, it causes confusion at call time, and in the end both end up underused.

### Step 2. Validate Role Justification

Check these three things:

1. **Purpose clarity**: Can you explain this agent's reason to exist in one sentence?
2. **Overlap**: Does it avoid overlapping 80% or more in responsibilities with an existing agent?
3. **Call frequency**: Is there a realistic need to call it at least once a week?

If a problem is found:

| Situation                         | Action                            |
| --------------------------------- | --------------------------------- |
| Role name has 3+ interpretations  | Ask a clarifying question, then wait |
| 80%+ overlap with existing agent  | Overlap warning + merge proposal  |
| Purpose is unclear                | Purpose-clarifying question + alternatives |
| Permission request poses a security risk | State the risks + propose a restricted alternative |
| Request to create 5+ at once      | Confirm priorities, then handle sequentially |

### Step 3. Clarifying Questions (if needed)

If the role name is ambiguous, clarify it with a question that includes choices.

```
Which scope does the "marketer" role cover?
A. Content marketing (blog, SEO)
B. Growth marketing (funnel analysis, A/B testing)
C. Full marketing (A+B combined)
```

### Step 4. Write the Agent Profile

Write the profile with 10 sections. Each section is needed so the agent clearly understands its role, authority, and limits, and behaves consistently. Omitting a section makes the agent act uncertainly in that area or exercise excessive autonomous judgment.

For a detailed guide to each section, see [agent-profile-template.md](references/agent-profile-template.md).

**The 10 sections:**

1. **Role Name** — Korean + English, with a one-line subtitle
2. **Mission** — reason to exist; the problem that arises without this role
3. **Responsibilities** — what to do + what not to do
4. **Authority & Limits** — areas of autonomous judgment + escalation conditions
5. **Input** — required/optional inputs and who provides them
6. **Output** — required output format, prohibitions
7. **Decision Principles** — top-priority values when making judgments
8. **Stop / Abort Rules** — situations requiring an immediate stop, and the action to take
9. **Communication Rules** — reporting format, expression rules
10. **Tone & Style** — tone, prohibited expressions, language setting

### Step 5. Configure the Frontmatter

Configure the agent markdown file's frontmatter to match the role's characteristics. **Always check the actual frontmatter format of an existing agent file first and follow the same format.** Claude Code and OpenCode use different frontmatter formats.

```bash
# Check existing agent format (use the path appropriate for your environment)
head -40 ~/.claude/agents/*.md 2>/dev/null
head -40 ~/.config/opencode/agents/*.md 2>/dev/null
```

For a detailed per-field guide, see [frontmatter-guide.md](references/frontmatter-guide.md).

**Claude Code environment:**

```yaml
---
name: [kebab-case-name]
description: |
  [1-2 sentence role description].

  <example>
  Context: [situation]
  user: "[request]"
  assistant: "[response]"
  <commentary>
  [why this agent is called]
  </commentary>
  </example>
model: inherit
color: [red|green|blue|yellow|cyan|magenta|white]
tools: ["Read", "Write", "Edit", "Bash", "Glob", "Grep"]
---
```

- `name`: a kebab-case name identical to the filename
- `description`: role description + three `<example>` blocks. The main session references this when selecting an agent
- `model: inherit`: inherits the main session's model
- `color`: a color to visually distinguish the agent in the terminal
- `tools`: the array of tools the agent can use

**OpenCode environment:**

```yaml
---
description: [role description - 1-2 sentences, including core responsibilities]
mode: subagent
temperature: [value suited to the role]
tools:
  [tools the role needs]
permission:
  [permissions suited to the role]
---
```

- `mode: subagent`: run as a subagent
- `temperature`: a value suited to the role (analysis/validation: 0.1-0.2, strategy/planning: 0.3-0.4, creative: 0.5-0.7)
- `tools`: per-tool true/false setting
- `permission`: per-tool allow/ask/deny setting

**Shared principles:**
- Don't use a different model per agent — it makes cost hard to predict and breaks output-quality consistency
- Least-privilege principle: enable only the tools the role needs

### Step 6. Present the Draft and Review

Present it to the user in this order:

**Part 1: Summary (3 lines or fewer)**

```
[Role name]: [one-line mission summary]
[List 3 core responsibilities]
[Relationship to / differentiation from existing agents]
```

**Part 2: The Agent Markdown File**

The system-prompt body, including the frontmatter + all 10 sections.

Ask the user for feedback: "How does this look overall? Let me know if there's anything you'd like to change."

### Step 7. Incorporate Feedback and Iterate

Revise the profile based on the user's feedback. Repeat this until the user is satisfied. Even when feedback is terse or abstract (e.g., "make it more aggressive"), figure out what the user actually wants and turn it into concrete edits.

### Step 8. Save the File

After user confirmation, save it to the appropriate path:

- Claude Code: `~/.claude/agents/{role-name-kebab-case}.md`
- OpenCode: `~/.config/opencode/agents/{role-name-kebab-case}.md`
- Project: save to both `.claude/agents/` and `.opencode/agents/`

Use lowercase, hyphen-separated filenames. E.g., `growth-marketer.md`, `senior-tech-lead.md`

---

## Improving an Existing Agent

This is the workflow for when the user asks to modify or improve an existing agent. Unlike "creating a new agent," it focuses on diagnosing the problems in an already-existing profile and improving it systematically.

### Step 1. Diagnosis

Read the existing agent file and measure its current quality with automated tools.

**Manual analysis:**
- Completeness of the current 10 sections — whether any section is missing
- Whether the frontmatter settings suit the role
- The relationship between the problem the user mentioned and the actual profile content

**Automated validation:**
```bash
# Structural validity check — produces a score out of 100
python -m scripts.validate_profile <agent-profile.md> --json

# Overlap analysis against other agents
python -m scripts.detect_overlap --threshold 0.3
```

Combine the two results and report the current "health score" to the user. Why this step matters: the root cause of the problem the user feels ("the tone is stiff") may lie elsewhere (e.g., missing escalation conditions → everything is decided autonomously → stiff tone).

### Step 2. Classify the Problems

Classify the diagnostic results into the following three categories and report them to the user:

| Category | Examples | Diagnostic basis |
|----------|----------|------------------|
| **Structural problems** | Missing sections, frontmatter errors, contradictions between sections | validate_profile.py results |
| **Content problems** | Unsuitable tone, vague responsibilities, too few/too many rules | Manual analysis + user feedback |
| **Relationship problems** | Role overlap with another agent, unclear boundaries | detect_overlap.py results |

Example report:
```
Current CS agent profile diagnosis (72/100):

[Structure] The Stop / Abort Rules section is empty — the agent decides everything autonomously
[Content] Tone & Style only says "professional and concise," which lacks specificity
[Relationship] 0.35 responsibility similarity with the junior-developer agent — the "bug triage" area overlaps

How should we prioritize?
1. Structural problems first (fill in the missing sections)
2. The problem you felt first (improve the tone)
3. All at once
```

When the user chooses, proceed in that order. Why offer choices: if the user said "just fix the tone" but you fix structural problems first, it diverges from their expectations.

### Step 3. Snapshot

Before starting the improvement work, preserve the original. It becomes the baseline for the before/after comparison after improvement.

```bash
# Copy the original into the workspace directory
cp <agent-profile.md> <workspace>/snapshot/<agent-name>-original.md

# Record the original's baseline validation score for later comparison
python -m scripts.validate_profile <workspace>/snapshot/<agent-name>-original.md --json \
  > <workspace>/snapshot/baseline-validation.json
```

Use a sibling directory of the agents directory for the workspace:
- Claude Code: `~/.claude/agents/<agent-name>-workspace/`
- OpenCode: `~/.config/opencode/agents/<agent-name>-workspace/`

### Step 4. Apply Improvements

After the user agrees, apply the changes. Clearly show before/after so the user can see the difference.

When improving, follow the principles in the "Writing Style Guide" section — reason-based explanations, generalization, concise but specific.

### Step 5. Validate and Compare

Confirm whether the improvement actually helped by re-running the static checks on the improved profile and comparing the results against the baseline captured in Step 3.

```bash
# Re-run structural validation on the improved profile
python -m scripts.validate_profile <agent-profile.md> --json

# Re-run overlap analysis to confirm the boundaries didn't regress
python -m scripts.detect_overlap --threshold 0.3
```

Compare against the baseline:
- **Validation score**: did the score out of 100 go up? Which checks that previously failed now pass?
- **Section completeness**: are the sections that were missing now filled in?
- **Overlap**: did the responsibility overlap with other agents stay the same or decrease? An improvement that introduces new overlap is a regression.

Report the before/after difference to the user — e.g., "72 → 89; the empty Stop / Abort Rules section is now filled; overlap with junior-developer dropped from 0.35 to 0.18."

If the user wants to finish quickly without a formal comparison ("I don't need the comparison"), you can skip this step — not every improvement needs a full re-validation.

### Step 6. Clean Up

When the user is satisfied with the improvement, clean up the snapshot and workspace. A leftover snapshot just takes up disk space and can later cause confusion ("Is this the current version?").

```bash
rm -rf <workspace>/
```

Confirm with the user before running it. There may be snapshot or comparison results in the workspace the user wants to keep, so don't delete without asking.

### When Iteration Is Needed

If one pass isn't satisfactory, repeat Steps 4-5:

1. Revise the profile based on feedback
2. Re-run `validate_profile` and `detect_overlap` on the revised profile
3. Compare the new score and overlap results against the baseline and the previous iteration
4. Repeat until satisfied
5. After finishing, run Step 6 (cleanup)

---

## Writing Style Guide

### Explain the Reasons

When writing an agent profile, instead of just listing rules, attach an explanation of why each rule is needed. Today's LLMs are smart enough that, once they understand the reason, they can judge correctly even in edge cases the rules don't cover. Conversely, coercive rules with no rationale prevent the model from responding flexibly.

**Good example:**
```markdown
Do not make the final deployment decision — that is the user's authority.
If the agent autonomously makes hard-to-reverse decisions, control becomes impossible.
```

**Has room for improvement:**
```markdown
Never make the final deployment decision
```

### Generalize

Don't fit too narrowly to a specific case. An agent profile is used repeatedly across many situations, so overfitting to one scenario makes it useless in others.

### Concise but Specific

- Use imperative/directive forms: "is", "does"
- Exclude emotional expressions: "I think...", "it's probably..." don't belong in a profile
- Attach the rationale: add a one-line "why?" to every design decision
- Korean by default; technical terms may include the English term (e.g., "subagent")

### Content Principles

- Don't do the agent's actual work on its behalf — this skill's job is to *define* the agent
- For a role that heavily overlaps an existing agent's responsibilities, warn the user and propose a merge
- Don't grant authority that infringes on the user's final decision-making power

### Coordination Between Agents

- Don't debate directly with other agents — all coordination goes through the user only. Allowing direct agent-to-agent communication removes the user from the decision-making flow.
- If you need to change an existing agent's responsibilities, report it to the user
- State uncertainties as uncertain, but offer your best judgment alongside

---

## Cross-Section Consistency Check

After finishing the profile, check the following. Why this check matters: if there are contradictions between sections, you can't predict which instruction the agent will follow.

| Check item                  | What to verify                                                  |
| --------------------------- | -------------------------------------------------------------- |
| Mission ↔ Responsibilities  | Is the role declared in the mission concretely reflected in the responsibilities? |
| Responsibilities ↔ Authority | Is authority granted to perform the "what to do" items?       |
| Authority ↔ Tools           | Are the tools matching the authority set in the frontmatter?   |
| Input ↔ Output              | Is the information received as input sufficient to produce the output? |
| Decision ↔ Stop Conditions  | Are situations unsolvable by the decision principles included in the stop conditions? |
| Communication ↔ Tone        | Do the communication rules and Tone & Style avoid contradicting each other? |

---

## Profile Validation

After writing a profile, you can validate its quality with automated tools. Run them from the agent-creator directory.

### Structural Validity Check

```bash
python -m scripts.validate_profile <agent-profile.md>
```

Checks frontmatter validity, the completeness of the 10 sections, and cross-section consistency, and produces a score out of 100. JSON output is available with the `--json` option.

### Overlap Analysis

```bash
python -m scripts.detect_overlap [--threshold 0.3]
```

Analyzes responsibility overlap among existing agents using Jaccard similarity. Prints an overlap warning for pairs at or above the threshold (default 0.3). This check becomes more important as the number of agents grows — overlapping roles cause confusion at call time and leave both underused.

### Agent Catalog

```bash
python -m scripts.catalog [--output catalog.md]
```

Generates a markdown overview of the entire agent organization: agent list, section completeness, overlap warnings, and tool-usage status. JSON output is available with the `--json` option.

---

## Reference Materials

### Reference Files
- [agent-profile-template.md](references/agent-profile-template.md) — detailed template for the 10 sections and a writing guide for each
- [frontmatter-guide.md](references/frontmatter-guide.md) — per-field explanation, recommended values, and examples for agent frontmatter
- [schemas.md](references/schemas.md) — JSON schema definitions for the agent catalog and overlap-analysis output

### Example Files
- [agent-example.md](examples/agent-example.md) — a complete, real example agent profile (growth marketer)

### Subagent Instructions
- `agents/overlap-analyzer.md` — how to analyze responsibility overlap between two agents
- `agents/profile-reviewer.md` — how to review profile quality

### Automation Scripts
- `scripts/validate_profile.py` — profile structural validity check
- `scripts/detect_overlap.py` — responsibility overlap analysis between agents
- `scripts/catalog.py` — generate the full agent catalog
