---
name: agent-orchestration
description: Use when the user asks to coordinate the work of multiple subagents or synthesize their results — e.g., "give me a briefing", "summarize the status", "coordinate the agents", "sort out task priorities", "summarize the overall situation", "distribute the work", "handle this using multiple agents", "who owns this?", "synthesize the agents' results", "show me the overall status", "lay out what's next", "orchestrate agents", "status briefing". Also use when the main agent, after analyzing a request, determines that: (1) it falls under a specific specialty area (DB, DevOps, security, QA, marketing, etc.) and should be delegated to a specialist subagent (including a single delegation); (2) it's a task that consumes a lot of the main session context — bulk file searches, log analysis, broad codebase investigation, web research across many items, organizing long material — and should be isolated in a subagent to save context; or (3) the request should be broken into small units (split across different specialty areas, or fanned out by repeating the same investigation across many items) so that two or more subagents process them in parallel/sequence and the main agent combines the results.
---

# Subagent Orchestration

Defines the workflow in which the main agent breaks a user request into specialized work units, delegates each unit to a suitable subagent, then combines and reports the results in the main session. Even for a single task, if it falls under a specialty area or would heavily consume the main session context, delegate it to a subagent to secure expertise and save the main context.

A subagent cannot invoke another subagent. Because decomposition, delegation, and combination must be performed by the main agent, this is structured as a skill.

Core principles:

- **Make delegation the default** — delegate if there's a gain in any one of expertise, context savings, or parallelism. But only delegate when the delegation gain exceeds the round-trip overhead.
- **Confine noise to the subagent and bring only conclusions to the main** — collect refined conclusions rather than raw data to protect the main session context.
- **Decompose → delegate → combine** — break a large request into small specialized units to process, and merge the partial results into one in the main session.

---

## Delegation Decision (3 Axes)

When you receive a request, **delegate to a subagent if any one** of the three axes below applies. Judge by the delegation gain, not by the number of agents.

1. **Expertise** — does it need the judgment or execution of a specific specialty area (DB, infrastructure, security, QA, marketing, customer support, etc.)? → Delegate to that specialist subagent even for a single task.
2. **Context cost** — is it a task that consumes the main session context at length, such as bulk file searches, log/data trawling, broad codebase investigation, or organizing long external material? → Isolate it in a subagent even for a single task to save the main context.
3. **Multiplicity** — does it span different specialty areas, does one task's output feed another's input, do multiple opinions need comparing/synthesizing, or does **the same kind of investigation/work repeat across many items** (N candidates, regions, products, etc.)? → Decompose the request and process it across multiple subagents in parallel/sequence.

**When not to delegate** (the over-delegation boundary):

- Simple, short tasks that can be answered immediately in the main session
- Trivial tasks where the delegation round-trip costs more than the task itself
- Tasks where the cost of conveying context is so high that it's faster for the main agent to handle them directly

→ Delegate only when the delegation gain (expertise, context savings, parallelism) exceeds the round-trip overhead. Don't delegate every task mechanically.

---

## Identifying Available Subagents

The subagent setup changes often (additions, edits, deletions). So **don't rely on a hardcoded list; explore the file system on each request to identify them dynamically.** Don't assume a particular agent exists.

Exploration procedure:

1. **Global agents** — check the `.md` files in the `~/.claude/agents/` and `~/.config/opencode/agents/` directories.
2. **Project agents** — also check the current project's `.claude/agents/` and `.opencode/agents/` directories.
3. Read each file's frontmatter (`name`, `description`) to identify its role and specialty area.
4. Map decomposition units against the identified list and draw up an invocation plan.

If there's no suitable specialist agent for a decomposed work unit, delegate to a general-purpose agent (`general`, etc.) or tell the user that a suitable agent is needed. Since the agent list differs by environment, always prioritize the actual setup confirmed by the exploration above.

---

## Orchestration Workflow

### Step 1: Decompose the Work

Once delegation is decided (especially the multiplicity axis), break the request into the smallest specialized units that can be processed independently.

Decomposition principles:

- **Single responsibility** — one unit handles only one specialty area and one purpose.
- **Clear input/output boundaries** — define what each unit takes as input and what it produces.
- **Maximize independence** — minimize dependencies between units so they can be processed in parallel as much as possible.
- **Specialty-area mapping** — assign each unit to the suitable subagent identified in the exploration above.

**Two forms of decomposition:**

- **Heterogeneous decomposition** — split across different specialty areas (e.g., PM + tech lead + marketer). Assign each unit to a different specialist agent.
- **Homogeneous fan-out** — repeat the same task across many items (e.g., researching N candidates, N regions, N products). Assign each item to a separate instance of the same agent type (e.g., the general-purpose research agent `researcher`) for parallel processing.

**fan-out quantitative threshold** — if the same kind of investigation/search/collection must repeat **three or more times**, don't run the loop directly in the main session; distribute it across subagents by item. If the main agent invokes dozens of web searches itself, its context drains fast and there's no capacity left for synthesis and judgment.

For a single delegation (only the expertise/context axes apply and there's no multiplicity), skip decomposition and delegate straight to that agent.

### Step 2: Draw Up the Invocation Plan

Identify the dependencies among the decomposed units to determine the invocation order:

```
Independent tasks → parallel invocation (multiple Task calls in a single message)
Dependent tasks → sequential invocation (include the previous result in the next prompt)
```

**Invocation plan format:**

```
[Parallel] product-manager: judge feature priorities / growth-marketer: analyze market viability
[Sequential] → senior-tech-lead: design the technical implementation direction based on the above results
[Sequential] → junior-developer: implement based on the tech lead's design
```

### Step 3: Invoke the Subagents

Elements to include in the prompt when invoking each subagent:

1. **Context**: the current situation and why this task is needed
2. **Specific instructions**: clearly, what to do
3. **Expected output format**: in what form the result should be returned
4. **Preceding agents' results** (for sequential invocation): the conclusions the previous agent reached
5. **Return-scope limit**: specify that it should return only refined conclusions and key points, not raw logs or full dumps. This is to save the main session context.

**Prompt example:**

```
Current situation: [context]
PM agent's judgment: [summary of the previous result]

Perform the following task:
- [specific instruction 1]
- [specific instruction 2]

Return the result in the following format (only refined conclusions, not raw data or full logs):
- Conclusion: [1–2 sentences]
- Rationale: [bullet points]
- Risks: [note if any]
```

### Step 4: Combine the Results

After collecting all subagents' results, handle them in one of two ways depending on the nature of the work.

- **Deliverable integration** — when partial deliverables must be merged into one finished product (integrating code modules, merging document sections, etc.). Verify boundary consistency, remove duplication and conflicts, check for omissions, then integrate.
- **Briefing** — when conveying judgments, status, or decisions to the user. Follow the output format below.

Synthesize subagent reports without distorting the originals.

---

## Output Formats

### Briefing Output (when conveying judgments, status, or decisions)

```
## Summary
- [key points, 1–3 lines]

## Decisions Needed
1. [Option A] -- [rationale, 1 line]
2. [Option B] -- [rationale, 1 line]
→ Recommendation: [recommended option] (reason: [1 line])

## Status
- In progress: [items]
- Blockers: [items]
- Done: [items]
```

### Deliverable Integration Output (when merging partial results into one)

```
## Completed Work
- [agent name]: [1-line summary of what was done]

## Integration Result
[the combined final deliverable or its location]

## Consistency Check
- Duplication/conflicts: [what was handled, or "None"]
- Omissions: [check result, or "None"]

## Follow-up Work (if any)
- [what needs to be done next]
```

---

## Conflict Mediation

When different agents' proposals conflict:

1. **Lay out both sides' rationale side by side** — editing the originals distorts the basis for judgment.
2. **Present one recommended option**, but state the rationale.
3. When both are valid, **ask the user to choose** — final decision authority rests with the user.

```
## Disagreement

### PM agent
- Claim: [content]
- Rationale: [rationale]

### Tech lead agent
- Claim: [content]
- Rationale: [rationale]

→ Recommendation: [option] (reason: [1 line])
→ Or: Both sides' rationale is valid. Requesting your decision.
```

---

## Prioritization Criteria

Apply the following criteria when ordering agent tasks. Higher in the list takes precedence.

1. **Directly tied to revenue** → top priority — work that directly affects revenue, conversion, or churn is tied to the survival of the business, so handle it first.
2. **Clearing blockers** → next — leaving items that block other work in place lets the bottleneck spread and lowers overall throughput.
3. **Urgency** → high priority — for time-limited items, missing the deadline makes the opportunity itself vanish, so start early.
4. **Scope of impact** → high priority — work affecting many users or features can raise overall value with a single improvement.
5. **Implementation cost** → favor items with high return on cost — handle work that yields big results with few resources first to maximize overall ROI.

---

## Escalation Rules

In the following situations, **immediately ask the user to decide**:

- **Decisions that incur cost** (tool subscriptions, external services, etc.) — incurring cost is hard to reverse, so prior approval is required.
- Priority changes that amount to a **change in product direction** — strategic judgment is outside the agent's authority, and only the user fully understands the business context.
- **When an inter-agent conflict has valid rationale on both sides** — if neither can be judged technically superior, a value judgment is needed, and that's the user's call.
- **When legal or ethical issues are involved** — the agent can't take on legal risk, and the consequences of a wrong judgment are severe.

---

## Prohibitions

- Do not make the **final decision** on the user's behalf — the agent's role is to organize information and recommend; the responsibility for deciding rests with the user.
- Do not **subjectively interpret or distort** agent reports — altering the originals risks the user judging on a wrong basis.
- No **emotional expressions** ("good news", "unfortunately", "I'm worried") — emotional expressions undermine the objectivity of the report and can bias the user's judgment.
- No **speculative expressions** ("probably", "it seems like") — speculation is hard to distinguish from fact and leads to decision errors. Convey only confirmed facts, mark uncertain information as "unconfirmed", and propose a way to verify it.

---

## Communication Tone

- Calm and structured. Convey only the essentials, no fluff.
- Always attach the rationale in one line.
- Keep each report to a **length the user can grasp within 2 minutes**.
- Batch non-urgent items into a single report.
