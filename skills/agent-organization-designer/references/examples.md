# Domain-Specific Organization Design Examples

A collection of worked examples showing that the principles in `SKILL.md` are not tied to any particular industry. When designing a new organization, pick the closest case as a starting point — but don't copy it verbatim; add or trim to fit the operator's actual bottlenecks. Every example assumes the simple "operator → all agents" reporting line.

## 1. Solo Content Creator (YouTube + Newsletter)

**Context**: One person doing everything from planning, filming, and editing to publishing and subscriber replies. The bottlenecks are repetitive research and post-publication replies.

**Design proposal (3 agents)**:

- **Research agent** — collects and summarizes topics, references, and competing content. (Purpose: cut planning time)
- **Publishing agent** — drafts titles, descriptions, tags, and newsletter copy. (Purpose: publishing speed)
- **Community agent** — classifies comments and inquiries, drafts replies, and turns recurring questions into FAQs. (Purpose: reduce reply load)

**Boundary note**: Creative core work like filming and editing is not delegated (the operator's own context). Research and publishing are split by "before/after publication".

## 2. Open-Source Maintainer

**Context**: Issues and PRs pour in and contributor replies pile up. The bottlenecks are triage and first-line replies.

**Design proposal (3 agents)**:

- **Issue-triage agent** — classifies new issues, labels them, detects duplicates, and requests reproduction info. (Purpose: reduce response delay on important issues)
- **Contributor-relations agent** — first-pass PR review comments and contribution-guide pointers. (Purpose: prevent contributor churn)
- **Release-notes agent** — collects and summarizes merged changes. (Purpose: reduce release workload)

**Boundary note**: Merge decisions and architecture judgments are escalated (hard-to-reverse decisions). Triage owns "issues" and relations owns "PRs", splitting the surface to avoid overlap.

## 3. Small Agency (Client Work)

**Context**: Several client projects running at once. The bottlenecks are tracking progress and first-pass review of deliverables.

**Design proposal (4 agents)**:

- **Project-tracker agent** — tracks progress, deadlines, and blockers; weekly summaries. (Purpose: save management time)
- **Deliverable-QA agent** — checklist review before delivery. (Purpose: reduce rework and complaints)
- **Client-communication agent** — drafts reports and inquiry replies. (Purpose: response speed and consistency)
- **Proposal agent** — drafts quotes and proposals for new inquiries. (Purpose: win-rate conversion)

**Boundary note**: Final contract and pricing decisions are escalated. The tracker (internal state) and communication (external outreach) are separated so tone and audience don't mix.

## 4. In-House Ops Team (Automating Repetitive Work)

**Context**: Data cleanup, reporting, and inquiry handling recur every week. The bottlenecks are producing standardized reports and first-line inquiry handling.

**Design proposal (4 agents)**:

- **Data-report agent** — collects periodic metrics and generates standardized reports. (Purpose: eliminate manual reporting)
- **Helpdesk agent** — classifies internal inquiries, gives first-line answers, and routes escalations. (Purpose: cut response time)
- **Documentation agent** — records and organizes processes and decisions. (Purpose: prevent knowledge loss)
- **Onboarding agent** — guides new hires and handles recurring questions. (Purpose: distribute onboarding load)

**Boundary note**: Sensitive decisions like HR and budget are escalated. The helpdesk (real-time) and documentation (asynchronous) are separated because their rhythms differ.

## 5. Research/Analysis (Individual or Small-Scale Research)

**Context**: Collecting, organizing, and synthesizing material repeats endlessly. The bottlenecks are broad first-pass collection and organization.

**Design proposal (3 agents)**:

- **Collection agent** — broadly gathers material and sources by topic and does a first-pass screening. (Purpose: save exploration time)
- **Organize/summarize agent** — structures, cross-checks, and summarizes collected material. (Purpose: shorten synthesis prep)
- **Writing-assist agent** — assists with drafts, citations, and formatting. (Purpose: output speed)

**Boundary note**: Final interpretation and conclusions are not delegated (the researcher's own judgment). Collection (breadth) and organization (depth) are split so one agent doesn't handle both shallowly.

---

Common patterns across these examples:

- Most start with **3–5 agents**.
- Work that is **hard to reverse or requires the operator's own context** — creative work, final judgments, sensitive decisions — is left to escalation rather than delegated.
- Agent boundaries are usually split along one of **stage (before/after), surface (target), or rhythm (real-time/asynchronous)**.
