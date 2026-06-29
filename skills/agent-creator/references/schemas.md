# JSON Schemas

This document defines the JSON schemas used by agent-creator.

---

## overlap_analysis.json

Output of the overlap-analyzer agent. Located at `analysis/overlap/{agent_a}-vs-{agent_b}.json`.

```json
{
  "agent_a": "growth-marketer.md",
  "agent_b": "content-strategist.md",
  "overlap_score": 0.45,
  "analysis": {
    "responsibility_overlap": [
      "Both include 'blog content planning' in their responsibilities",
      "Both perform 'SEO keyword analysis'"
    ],
    "description_similarity": {
      "confusing": true,
      "detail": "Both descriptions use 'content' and 'optimization' as core keywords"
    },
    "authority_conflicts": [
      "Both have write: true, granting permission to create markdown files"
    ],
    "io_overlap": {
      "input_overlap": ["Both take 'target keywords for analysis' as input"],
      "output_overlap": ["Both produce output in a 'content calendar' format"],
      "pipeline_relationship": false
    },
    "boundary_conflicts": [
      "The marketer's 'drafting copy' and the strategist's 'drafting content' are effectively the same task"
    ],
    "recommendation": "Merge proposal: combine the two roles into 'Growth Content Marketer'"
  },
  "merge_draft": {
    "role_name": "Growth Content Marketer",
    "mission": "Plan, produce, and distribute content based on data, and measure performance to optimize user acquisition and conversion",
    "key_responsibilities": [
      "SEO keyword analysis and content topic selection",
      "Drafting blog/landing-page content",
      "Tracking and optimizing content performance metrics"
    ]
  }
}
```

**Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `agent_a` | string | Required | filename of the first agent |
| `agent_b` | string | Required | filename of the second agent |
| `overlap_score` | number | Required | overlap score (0.0 - 1.0) |
| `analysis.responsibility_overlap` | array | Required | list of overlapping responsibilities |
| `analysis.description_similarity` | object | Required | description similarity analysis |
| `analysis.description_similarity.confusing` | boolean | Required | whether confusion is possible at call time |
| `analysis.description_similarity.detail` | string | Required | detailed explanation of the similarity |
| `analysis.authority_conflicts` | array | Required | list of authority conflicts |
| `analysis.io_overlap` | object | Required | input/output overlap analysis |
| `analysis.io_overlap.input_overlap` | array | Required | overlapping inputs |
| `analysis.io_overlap.output_overlap` | array | Required | overlapping outputs |
| `analysis.io_overlap.pipeline_relationship` | boolean | Required | whether there is a pipeline relationship (if true, it's collaboration, not overlap) |
| `analysis.boundary_conflicts` | array | Required | list of boundary conflicts |
| `analysis.recommendation` | string | Required | merge proposal or boundary-clarification proposal |
| `merge_draft` | object | Optional | included only for a merge proposal (overlap_score > 0.40) |
| `merge_draft.role_name` | string | Optional | the merged role name |
| `merge_draft.mission` | string | Optional | the merged mission |
| `merge_draft.key_responsibilities` | array | Optional | the merged list of core responsibilities |

---

## catalog.json

The full catalog of the agent organization. Located at `analysis/catalog.json`.

```json
{
  "updated_at": "2026-03-06T10:30:00Z",
  "total_agents": 5,
  "agents": [
    {
      "name": "growth-marketer",
      "file_path": "~/.claude/agents/growth-marketer.md",
      "scope": "global",
      "description": "Growth marketer. Optimizes user acquisition/conversion/retention based on data.",
      "mission_summary": "Data-driven user acquisition/conversion optimization",
      "key_responsibilities": [
        "Tracking core metrics and generating reports",
        "A/B test design and analysis",
        "ROI comparison by channel"
      ],
      "temperature": 0.5,
      "tools": {
        "read": true,
        "write": true,
        "edit": true,
        "glob": true,
        "grep": true,
        "bash": false
      },
      "review_score": 85
    },
    {
      "name": "senior-tech-lead",
      "file_path": "~/.claude/agents/senior-tech-lead.md",
      "scope": "global",
      "description": "Senior tech lead. Proactively identifies technical risks and validates architecture choices.",
      "mission_summary": "Technical-risk identification and architecture validation",
      "key_responsibilities": [
        "Architecture design and validation",
        "Tech-stack selection guidance",
        "Code review and quality-standard setting"
      ],
      "temperature": 0.2,
      "tools": {
        "read": true,
        "write": true,
        "edit": true,
        "glob": true,
        "grep": true,
        "bash": true
      },
      "review_score": null
    }
  ],
  "overlap_pairs": [
    {
      "agent_a": "growth-marketer",
      "agent_b": "content-strategist",
      "overlap_score": 0.45,
      "recommendation": "Merge proposal"
    }
  ]
}
```

**Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `updated_at` | string | Required | ISO timestamp of the catalog update |
| `total_agents` | number | Required | total number of registered agents |
| `agents[]` | array | Required | list of agents |
| `agents[].name` | string | Required | agent name (kebab-case) |
| `agents[].file_path` | string | Required | path to the profile file |
| `agents[].scope` | string | Required | `"global"` or `"project"` |
| `agents[].description` | string | Required | the frontmatter description |
| `agents[].mission_summary` | string | Required | one-line summary of the mission |
| `agents[].key_responsibilities` | array | Required | 3-5 core responsibilities |
| `agents[].temperature` | number | Required | the frontmatter temperature |
| `agents[].tools` | object | Required | the frontmatter tools setting |
| `agents[].review_score` | number\|null | Required | profile reviewer's total score (null if not evaluated) |
| `overlap_pairs[]` | array | Required | list of overlap-analysis results |
| `overlap_pairs[].agent_a` | string | Required | name of the first agent |
| `overlap_pairs[].agent_b` | string | Required | name of the second agent |
| `overlap_pairs[].overlap_score` | number | Required | overlap score (0.0 - 1.0) |
| `overlap_pairs[].recommendation` | string | Required | summary of the recommendation |
