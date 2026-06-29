---
name: agent-organization-designer
description: Design and audit an AI agent organization. Use when planning the overall composition, priorities, role boundaries, and scale of an entire agent organization — e.g., "plan out which agents I need", "set up an agent team/organization", "sort out the role split among agents", "I have too many agents, consolidate and clean them up", "design an agent org to handle ○○ work" — or when auditing and restructuring an existing agent organization. The focus is organization-level design — "which agents do I need" — not writing the profile (system prompt) of an individual agent. Use proactively whenever the user mentions an agent organization, team, composition, or role split, even if they don't use the word "design".
---

# AI Agent Organization Design

This skill helps you decide "which agents do I need?" It is not about writing an individual agent's profile (system prompt) word by word, but **organization-level design**: surveying the whole organization to divide roles, draw boundaries, and set priorities. Writing individual profiles is the job of a separate tool (e.g., an agent-creation skill like `agent-creator`), so once the design is settled, hand creation off to that tool.

This skill is not tied to any particular industry or organizational form. It applies to any context where "work is divided among multiple AI agents": a solo creator running content, an open-source maintainer managing issues, a small agency handling client work, an in-house team automating repetitive tasks, and so on. In this document, the **operator** refers to the party (whether an individual or a team) responsible for the agent organization and delegating work to it.

## First Step: Figure Out Where the User Stands

Requests usually fall into one of four branches. Identify which one first, then proceed together from there.

- "I want to build an agent team from scratch" → [Designing a New Organization](#designing-a-new-organization)
- "I have several agents now but they're a mess" → [Auditing an Existing Organization](#auditing-an-existing-organization)
- "Area ○○ is weak — what should I add?" → Partial reinforcement (a scaled-down version of the audit flow)
- "I have too many agents and want to cut down" → Consolidation and cleanup (the audit flow)

Don't rush to dump a list of agents. Without knowing the operator's current situation, you end up with an over-designed (unnecessary agents) or under-designed (uncovered areas) organization.

---

## Core Principles

A good agent organization is not a flashy org chart but one that **reduces the operator's cognitive load**. Every principle below derives from that single goal. Resources (time, attention, management capacity) are always finite, and usually the scarcest resource is the operator's decision-making time.

### 1. Justify the purpose — every agent must prove why it exists

Each agent is one more surface the operator has to manage. So every agent must have a clear path to contributing to the organization's goal. What the goal is varies by context — it could be revenue, the volume or quality of output, processing speed, or reach. The key question is always the same:

> "What gets worse if this agent doesn't exist?"

If you can't answer this concretely, put that agent on hold.

- **Good example**: an issue-triage agent — classifies and labels new issues so the maintainer responds to what matters first (reduces response delay)
- **Bad example**: an "inspiration agent" — its contribution path is vague, leaving only management cost

### 2. Save the operator's time — if an agent becomes a burden, the means defeats the end

The purpose of an agent is to relieve the operator's decision-making and execution burden. But as agents multiply, the very act of judging "who should I assign this to?" becomes a new burden. So a structure where a few roles cover a broad scope is almost always better than one where many roles are narrowly split.

### 3. Minimal organization — merge whatever can be merged

Fewer agents is better. Before adding a new agent, first ask "can't I just widen an existing agent's responsibilities?" Unless there's a clear reason to split (different rhythms, domains, or risk levels — see the split signals in `references/scaling.md`), keep it as one.

### 4. Clear boundaries — overlap causes conflict

When two agents' responsibilities overlap, they compete over the same request or duplicate work, and the operator is again left wondering "who?". Make sure each agent's area doesn't overlap with the others, and that together they leave no gaps.

### 5. Simple reporting lines — don't build a hierarchy

Every agent reports directly to the operator. A structure where one agent "manages" another makes debugging hard and blurs accountability. When coordination is needed, it's handled by the operator (or a separate orchestration layer), not by a hierarchy among agents.

---

## Designing a New Organization

For when there's no agent organization yet, or you're rebuilding from scratch.

### Step 1. Assess the current situation

Check the following. If you don't know, ask the operator — don't design on guesswork.

1. **Goal**: What must this organization ultimately contribute to? (revenue, output volume, quality, speed, reach, etc.)
2. **What the operator currently does by hand**: a list of repetitive tasks
3. **Bottlenecks**: among those, the tasks that take the most time or that get put off the most
4. **Scale and maturity**: whether the repetitive work is 1–2 kinds or has branched into many — the right number of agents changes accordingly (`references/scaling.md`)
5. **Existing automation**: tools and scripts already in use (to avoid duplication)

### Step 2. Identify delegable roles

From the operator's task list, sift out what's worth handing to an agent. Not every task is suitable for delegation.

| Criterion | Good to delegate | Poor to delegate |
|------|-----------|-------------|
| Repetitiveness | A similar pattern recurs periodically | A wholly new judgment each time |
| Specialization | Handled with specific domain knowledge | Requires broad context only the operator has |
| Risk level | A mistake can be undone | A decision that's hard to reverse |
| Time consumption | Steadily eats into the operator's time | Once in a while, done in five minutes |

Keep tasks closer to the right column in the operator's own hands, and bundle tasks closer to the left into agents.

### Step 3. Bundle roles into agents

Group the identified roles into agents.

1. **Bundle by function**: "analysis" and "the execution based on that analysis" are usually better as one agent. E.g., channel performance analysis + copywriting → a single marketing agent.
2. **Start with 3–5**: don't build 10 from the outset. Let the operator temporarily cover uncovered areas, and add agents when bottlenecks become clear.
3. **Give each agent a one-line mission**: if it can't be described in a single sentence, its responsibilities are too broad or too vague.

Present the design in the following format (fill it in as is):

```
## Agent Organization Design Proposal

### 1. [Role name]
- Core mission: [one line]
- Responsibilities: [2–3]
- Goal contribution: [the concrete path linking to the organization's goal]
- Priority: [high/medium/low]

### 2. [Role name]
...

### Role Boundary Map
[Which request goes to which agent — spell out the boundary cases likely to cause confusion]

### Escalation Flow
[Which situations/decisions must go straight to the operator without passing through an agent]
```

Don't omit the boundary map and the escalation flow. Without these two, the operator ends up re-deciding "who should I assign this to?" and "is this something I need to look at?" every time.

### Step 4. Set priorities

You don't need to build everything at once. Set the order by the following.

1. **Savings**: how much of the operator's time and load does this agent relieve?
2. **Goal impact**: does it affect the organization's goal immediately, or is the effect long-term?
3. **Implementation difficulty**: is the profile simple to write, or does it require deep domain knowledge?

Build the agents with **big savings + big impact + low difficulty** first. Queue up the rest and proceed when bottlenecks actually surface.

### Step 5. Delegate creation

Once the design is settled, hand off writing the individual agent profiles to a separate tool (e.g., an agent-creation skill like `agent-creator`). Pass along the following, organized:

- Role name and one-line mission
- Scope of responsibilities
- Boundaries with other agents (the boundary map from Step 3)
- Escalation conditions (which decisions must go up to the operator)

This skill is responsible up to **what to build**; it hands off **how to write it** to the creation tool.

---

## Auditing an Existing Organization

For when an agent organization already exists and needs auditing, improvement, or cleanup. Requests like "there are too many agents", "the roles overlap", or "○○ is uncovered" fall here.

### Step 1. Gather the current state

Read the existing agent definitions to build the full picture. The location of agent definition files varies by tool — e.g., global `~/.claude/agents/` and `~/.config/opencode/agents/`, project `.claude/agents/` and `.opencode/agents/`. Confirm the location with the operator or check the known paths.

From each agent, extract the following and collect it in one place:

- Role name, description, and 2–3 core responsibilities
- Areas that appear to overlap with other agents
- Uncovered areas no one is responsible for

> If there are too many agents to read through one by one, split them across subagents by item and collect only the summaries (saving the main context).

### Step 2. Diagnose organizational health

Look from five angles.

| Angle | Healthy | Warning sign |
|------|------|-----------|
| **Coverage** | All key repetitive tasks are assigned | Uncovered areas — the operator keeps doing them by hand |
| **Duplication** | Areas are clearly distinct from each other | Two or more cover the same area |
| **Balance** | Workload is evenly distributed | Responsibilities over-concentrated in one agent |
| **Purpose linkage** | Every agent's contribution path is clear | An agent whose reason to exist is vague |
| **Scale** | A count matching the breadth of repetitive work | Too many (management burden) / too few (gaps) |

For scale criteria and the add/merge/split/remove heuristics, see `references/scaling.md`.

### Step 3. Propose improvements

Report the diagnosis to the operator and propose concrete actions. There are five levers:

- **Add**: a new agent for an uncovered area
- **Merge**: combine overlapping agents (the minimal-organization principle)
- **Split**: divide an over-concentrated agent into two — but only when there's a clear split signal (different rhythms, domains, or risk levels)
- **Remove**: retire an agent whose goal contribution is vague
- **Adjust boundaries**: redistribute responsibilities so there's no overlap or gap

Attach a "why" to each action. The operator has to be convinced to actually apply it. After getting agreement, delegate the creation and modification of individual agents to the creation tool.

---

## Organization Scale Guide

The right number of agents varies with the breadth of repetitive work and operational maturity. The below is only a starting point; the final criterion is always "do I really need this agent?" Stage-by-stage recommended setups and domain-specific examples are in `references/scaling.md` and `references/examples.md`.

- **1–2 kinds of repetitive work (starting)**: 1–2 agents. Don't spend time on design; focus on core output.
- **Expanding into several branches**: 3–5 agents. Quickly verify which area is actually the bottleneck.
- **Specialization by area**: 5–7 agents. Add depth to validated areas.
- **Standardization and organization**: 7–10+ agents. Refine boundaries and periodically prune duplication.

As the count grows, the "minimal organization" and "clear boundaries" from the [Core Principles](#core-principles) matter more — the larger the organization, the more regularly you run consolidation and cleanup audits.

---

## Relationship with the Creation Tool

This skill is the **planning** layer; the agent-creation tool (e.g., `agent-creator`) is the **execution** layer.

| This skill (agent-organization-designer) | Creation tool (e.g., agent-creator) |
|------------------------------|------------------------------|
| Which agents do I need? | How do I write that agent's profile? |
| Boundaries, priorities, and scale across roles | A single agent's prompt, frontmatter, and behavior |
| Organization-level audit and restructuring | Individual-agent-level diagnosis and improvement |

When planning is done, hand the creation tool the role name, mission, scope of responsibilities, boundaries, and escalation conditions, and let it handle creation. Conversely, quality issues with an individual agent (awkward tone, failing to escalate, etc.) go to the creation tool's improvement flow, not this skill.

---

## References

- `references/scaling.md` — recommended setups by organization scale/maturity stage, and criteria for adding/merging/splitting/removing
- `references/examples.md` — worked organization-design examples by domain (solo creator, open-source maintainer, small agency, in-house ops team, research)
