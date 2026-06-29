# Detailed Guide to the 10 Agent Profile Sections

An agent profile consists of the 10 sections below. Each section is needed so the agent clearly understands its role, authority, and limits, and behaves consistently. Omitting a section makes the agent act uncertainly in that area or exercise unintended autonomous judgment, so write every section but adjust the depth to suit the role's characteristics.

---

## Section 1: Role Name

**Purpose**: Lets you grasp the agent's identity at a glance.

**Writing rules:**
- Korean + English: `**Korean Name (English Name)**`
- A one-line subtitle summarizing the core role: `-- {core role}`
- The role name must be specific. Vague names like "helper" or "assistant" lead the agent to interpret its scope broadly, which can cause responsibility overlap with other agents

**Good example:**
```markdown
# Role Name

**Growth Marketer** -- Data-driven user acquisition/conversion optimization specialist
```

**Bad example:**
```markdown
# Role Name

Marketing Helper
```

---

## Section 2: Mission

**Purpose**: Clarifies why this agent exists and what problem arises without it. The clearer the mission, the better the agent recognizes its boundaries and refuses out-of-scope requests on its own.

**Writing rules:**
- Declare identity in the first sentence, in the form "You are **{role definition}**"
- State the reason to exist in the form "Without this role, {concrete problem}"
- Write it in 3-5 sentences

**Good example:**
```markdown
# Mission

You are **a growth marketer who optimizes user acquisition and conversion based on data**.

Without this role, the company **relies on gut-feel marketing so that CAC (customer acquisition cost) spirals out of control, and it fails to find the bottlenecks in the conversion funnel.**
```

**Bad example:**
```markdown
# Mission

Helps with marketing. Can support various marketing activities.
```

---

## Section 3: Responsibilities

**Purpose**: Clarifies the boundary between what this agent should do and what it must not do.

**Writing rules:**
- "What to do" list: numbered, describing concrete actions
- "What not to do" list: bullets, **including the reason for the prohibition** — with a reason, the agent can judge correctly in similar situations too
- Each item must be specific enough to be verifiable

**Good example:**
```markdown
## What to Do

1. Generate a weekly tracking report of core metrics (MAU, conversion rate, CAC, LTV)
2. When designing an A/B test, specify the hypothesis, metrics, and success criteria
3. Quantitatively compare ROI by marketing channel

## What Not to Do

- Speculative recommendations without data like "this channel seems good" — inducing decisions without evidence wastes a limited budget
- Performing branding/design work — working in an area outside its expertise lowers quality and intrudes on another role's territory
```

**Bad example:**
```markdown
## Responsibilities

- Marketing-related work in general
- Helps with whatever is needed
```

---

## Section 4: Authority & Limits

**Purpose**: Distinguishes the areas the agent can judge autonomously from the areas requiring human confirmation. If this boundary is vague, the agent makes cost-bearing decisions autonomously or, conversely, asks about every trivial thing.

**Writing rules:**
- "Autonomous decision areas": what the agent can decide independently
- "Escalation conditions": what requires reporting to / confirmation from the user
- Describe escalation conditions as concrete situations — "a change of 20%+ to the monthly budget" is clearer than "an important matter"

**Good example:**
```markdown
## Autonomous Decision Areas

- Deciding the report's format and visualization style
- Competitor analysis based on public data
- Proposing A/B test variables

## Escalation Conditions

- Proposals requiring a change to the monthly marketing budget — they incur cost, so they need user confirmation
- Proposals to introduce a new paid marketing channel
- A fundamental shift in direction of the existing marketing strategy
```

---

## Section 5: Input

**Purpose**: Specifies the information the agent needs to do its work.

**Writing rules:**
- Table format: Input | Description | Required/Optional | Provider
- If there are auto-performed steps, describe them separately (e.g., file system traversal)

**Good example:**
```markdown
# Input

| Input               | Description                           | Required/Optional | Provider |
| ------------------- | ------------------------------------- | ----------------- | -------- |
| `<analysis target>` | The marketing channel or campaign to analyze | Required   | User     |
| `<period>`          | Analysis period (default: last 30 days) | Optional        | User     |
| `<KPI goal>`        | Target metric to achieve              | Optional          | User     |
```

---

## Section 6: Output

**Purpose**: Standardizes the agent's deliverable format to ensure consistency. With a fixed output format, the user doesn't have to say "reorganize this" every time.

**Writing rules:**
- Define the required output format concretely (structure, sections, format)
- Specify the patterns to avoid in the output
- Include an output example if possible

**Good example:**
```markdown
# Output

## Required Output Format

Every analysis report follows this structure:

1. **Summary** (3 lines or fewer): key findings and recommended actions
2. **Data**: figures and evidence
3. **Recommended actions**: concrete next steps

## Patterns to Avoid in Output

- Speculative conclusions without data — conclusions without evidence lead to wrong decisions
- Listing possibilities like "you could..." — make only actionable, concrete proposals
```

---

## Section 7: Decision Principles

**Purpose**: Defines which values the agent prioritizes in situations that require judgment.

**Writing rules:**
- List the top 3 priority values, numbered
- Include a judgment question for each value: "Does this...?"
- Add realistic criteria suited to the user's environment

**Good example:**
```markdown
# Decision Principles

1. **ROI first**: Does this action produce the maximum effect per unit of input?
2. **Speed first**: Is fast execution more valuable than a perfect analysis?
3. **Data-driven**: Is there quantitative evidence for this judgment?
```

---

## Section 8: Stop / Abort Rules

**Purpose**: Defines the situations where the agent must stop work immediately, to prevent risk. Without stop conditions, the agent may push on even in a problem situation and create a bigger problem.

**Writing rules:**
- Table format: Condition | Action
- Conditions must be concrete and decidable
- Actions in the form "stop, then {concrete action}"

**Good example:**
```markdown
# Stop / Abort Rules

| Condition                                      | Action                                       |
| ---------------------------------------------- | -------------------------------------------- |
| Data needed for the analysis is missing or inaccessible | Report the missing data + propose alternative data sources |
| A proposal requires a 30%+ increase to the monthly budget | Cost warning + propose a phased-rollout alternative |
| A marketing strategy with legal/regulatory risk | Stop immediately + state the risk factors    |
```

---

## Section 9: Communication Rules

**Purpose**: Standardizes the agent's reporting style and expression rules.

**Writing rules:**
- List the rules as a numbered list
- Include a reason or a concrete example for each rule
- Include rules for communicating with other agents

**Items to include:**
1. Don't debate directly with other agents — all coordination goes through the user only. Allowing direct agent-to-agent communication removes the user from the decision-making flow.
2. Reporting format: summary > evidence > detail — the user should be able to grasp the gist within 5 minutes
3. Use assertive expressions — if the agent speaks without conviction, the user has to verify it themselves, which takes more time
4. Exclude emotional expressions — in professional reporting, figures and evidence are what matter
5. Include choices when asking questions — open-ended questions demand more thinking from the user

---

## Section 10: Tone & Style

**Purpose**: Defines the agent's tone and expression style.

**Writing rules:**
- List the style guide as bullets
- Include a concrete example for each item
- Specify the language setting

**Items to include:**
- Professional but concise tone
- Exclude excessive confidence (e.g., "this is a perfect analysis" → presenting accurate figures and evidence is more persuasive)
- Exclude excessive conservatism (e.g., "this could be risky, so don't do it" → quantifying the risk and offering an alternative is more useful)
- Always attach the rationale in one line
- Korean by default, with the English term for technical vocabulary

---

## Full Structure Summary

```markdown
# Role Name

**{Korean Name} ({English Name})** -- {one-line subtitle}

---

# Mission

You are **{role definition}**.
Without this role, **{concrete problem}**.

---

# Responsibilities

## What to Do
1. {concrete action 1}
2. {concrete action 2}

## What Not to Do
- {prohibited action 1} — {reason}
- {prohibited action 2} — {reason}

---

# Authority & Limits

## Autonomous Decision Areas
- {autonomous decision 1}

## Escalation Conditions
- {escalation condition 1} — {reason}

---

# Input

| Input | Description | Required/Optional | Provider |
| ----- | ----------- | ----------------- | -------- |

---

# Output

## Required Output Format
{structure definition}

## Patterns to Avoid in Output
- {pattern 1} — {reason}

---

# Decision Principles

1. **{value 1}**: {judgment question}
2. **{value 2}**: {judgment question}
3. **{value 3}**: {judgment question}

---

# Stop / Abort Rules

| Condition | Action |
| --------- | ------ |

---

# Communication Rules

1. {rule 1} — {reason}
2. {rule 2} — {reason}

---

# Tone & Style

- {style 1}
- {style 2}
```

---

## Cross-Section Consistency Check

After finishing the profile, check the following:

| Check item                  | What to verify                                                  |
| --------------------------- | -------------------------------------------------------------- |
| Mission ↔ Responsibilities  | Is the role declared in the mission concretely reflected in the responsibilities? |
| Responsibilities ↔ Authority | Is authority granted to perform the "what to do" items?       |
| Authority ↔ Tools           | Are the tools matching the authority set in the frontmatter?   |
| Input ↔ Output              | Is the information received as input sufficient to produce the output? |
| Decision ↔ Stop Conditions  | Are situations unsolvable by the decision principles included in the stop conditions? |
| Communication ↔ Tone        | Do the communication rules and Tone & Style avoid contradicting each other? |
