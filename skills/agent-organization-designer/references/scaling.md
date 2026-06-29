# Organization Scale and Maturity Guide

Expands on the "Organization Scale Guide" in `SKILL.md`. The number of agents is a function of the **breadth of repetitive work** and **operational maturity**. The stages below are a starting point; the final criterion is always "do I really need this agent?"

## Recommended Setup by Stage

Stages are divided not by product or revenue but by **the number of distinct branches of repetitive work the operator handles**.

### Stage 1 — Starting (1–2 kinds of repetitive work)

- **Recommended count**: 1–2
- **Typical first picks**: an execution agent (producing repetitive output), a collection agent (gathering feedback and material)
- **Key point**: Don't spend time on organization design. Focus on the output itself, and add agents when bottlenecks surface.

### Stage 2 — Expanding (work in several branches)

- **Recommended count**: 3–5
- **Candidates to add**: an analysis/experiment agent (verifying what works), a prioritization agent (sorting out what to do first)
- **Key point**: Quickly identify which area is the real bottleneck. Still breadth over depth.

### Stage 3 — Specialization (area-specific expertise needed)

- **Recommended count**: 5–7
- **Candidates to add**: domain-specialist agents (deepening a specific area such as quality, tech, or content)
- **Key point**: Add depth to validated areas. Boundary overlap starts appearing around now, so begin auditing.

### Stage 4 — Organizing (standardization needed)

- **Recommended count**: 7–10+
- **Candidates to add**: a data/metrics agent, finer-grained area specialists
- **Key point**: Refine boundaries and prune duplication regularly. The range where scale itself becomes a management burden.

These numbers aren't absolute. An organization managed by one person can have fewer at the same stage, while one run by a team can have more.

## Add Decision

Before creating a new agent, ask in order:

1. Can widening an existing agent's responsibilities cover it? → If so, don't add one.
2. Does this area steadily eat into the operator's time? → If it's only once in a while, do it by hand.
3. Can it be described with a one-line mission? → If not, the scope is vague. Split it further or redefine it.

## Merge Decision

Consider merging two agents when:

- The same request often applies to both (the boundary is blurry).
- Both look at the same data and context.
- One side's workload is too small to justify a standalone agent.

## Split Decision

Conversely, when two or more of the following "split signals" coincide, divide one agent into two:

- **Different rhythms**: one is real-time response, the other is weekly work.
- **Different domains**: the required expertise diverges (e.g., technical diagnosis vs. customer communication).
- **Different risk levels**: one is easy to reverse, the other needs careful approval.
- **Over-concentration**: one agent has so many responsibilities that its mission won't fit in one line.

If there's only one split signal, it's usually better to keep them together — the minimal-organization principle outweighs the benefit of splitting.

## Remove Decision

- You can't concretely answer "what gets worse if this agent doesn't exist?"
- Its recent invocation frequency is effectively zero.
- It's naturally absorbed by the expansion of another agent's responsibilities.
