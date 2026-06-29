# Instruction Refactoring Guide

Summarizes detailed per-type procedures for instruction refactoring, how to audit, and the order of execution.

> Refactoring is classified as a **significant edit**. Always propose the change plan to the user and proceed only after approval. — Meaning must be preserved, and only the user can make the final call on "what this rule was intended to do".

---

## Refactoring Types

| Type                          | Description                                                  | Example                                            |
| ----------------------------- | ----------------------------------------------------------- | -------------------------------------------------- |
| **Deduplication**             | Merge identical or similar rules scattered across multiple places into one | The same content repeated in global and workspace instructions |
| **Structure improvement**     | Reorganize when related rules are scattered or the logical flow is off | A Git-related rule wedged inside the testing section |
| **Verbosity compression**     | Rewrite needlessly verbose or repetitive explanations to be concise | The same point restated three times in different words |
| **Layer reallocation**        | Move rules misplaced between global/workspace to the right layer | A project-agnostic rule that exists only in the workspace |
| **Identifying obsolete rules** | Identify and report rules that are no longer valid          | A rule for a removed tool still lingers            |
| **Cross-agent inconsistency** | Unify global instructions written differently per agent     | Claude Code and OpenCode global rules mean different things |

---

## Refactoring Procedure

### 1. Audit

Read both the global and workspace instructions and compare the global instruction files across active agents. Grasping the full picture lets you catch every duplicate or contradiction. Identify the following:

| Item to Identify     | How to Check                                      |
| -------------------- | ------------------------------------------------- |
| **Duplication**      | Compare full text for content that exists in multiple places |
| **Contradiction**    | Check for rules that conflict with each other     |
| **Verbosity**        | Check for long explanations that can be compressed |
| **Structural issues** | Check for placements that don't logically fit    |
| **Obsolescence**     | Check for rules that no longer match the current code/tools |
| **Agent inconsistency** | Check whether the same rule is described differently per agent |

### 2. Plan

Turn the issues found into a concrete change plan so the user can decide whether to approve.

- Lay out a fix for each issue found.
- Specify the **before/after** of each change.
- List the affected agent files.

Example:

```
[Deduplication] Git commit message rule
- Location: AGENTS.md line 15, ~/.claude/CLAUDE.md line 42
- Before: both contain "Write commit messages in Korean"
- After: keep only in AGENTS.md, remove from CLAUDE.md
- Impact: CLAUDE.md (auto-reflected since it is an @ reference)
```

### 3. Approve

Since meaning preservation is the crux of refactoring, the user must confirm the intent of each change.

- Present the change plan to the user for approval.
- For obsolete rules, explicitly confirm **whether to delete** with the user.
- Get staged approval for large changes, split by type. — Approving everything at once makes it hard for the user to review individual changes.

### 4. Execute

Apply only approved changes. Apply them in order from safest first, so that even if a problem arises mid-way the rollback scope stays minimal.

Execution order:

1. **Deduplication** (safest — merging identical content into one place, so the risk of information loss is low)
2. **Structure improvement** (moving/reordering sections)
3. **Verbosity compression** (requires verifying meaning is preserved)
4. **Layer reallocation** (moving between files)
5. **Handling obsolete rules** (delete/retain)
6. **Resolving cross-agent inconsistency**

For each stage:
- **Workspace**: edit `AGENTS.md` → verify `@` references → update synced files
- **Global**: edit each active agent's global instruction file

### 5. Verify

After refactoring, verify there is no change in meaning or loss of information.

| Verification Item                        | How to Check                   |
| ---------------------------------------- | ------------------------------ |
| Is each rule's meaning identical before and after? | Compare before/after  |
| Is there no information loss?            | Every rule from the original is present in the result |
| Are all active agent files intact?       | Read each file to confirm      |
| Are the `@`-reference files correct?     | Confirm they contain only the one reference line |
| Is there no contradiction between global and workspace? | Cross-check rules on both sides |

---

## Refactoring Principles in Detail

### Meaning Preservation

- After refactoring, **every rule must mean the same thing**. — This is the fundamental difference between refactoring and editing.
- Even when compressing a rule, always keep the **key directives and examples**.
- Get user confirmation for wording changes that might subtly shift the meaning.

### Preventing Information Loss

- When removing duplicates, merge them so that **information unique to each version is not lost**.
- Example: if file A has "commit messages in Korean" and file B has "commit messages in Korean + scope required", the merged version must include "scope required".

### Incremental Application

- Do not do a large refactor all at once. — Changing everything together makes it hard to trace which stage went wrong when a problem occurs.
- Apply it **in stages**, split by type.
- After each stage, run verification and proceed to the next stage only if there are no problems.

### Handling Obsolete Rules

- Even a rule that doesn't match the current code may carry **future intent**. — e.g., deleting a "migration planned later" rule erases that intent.
- Always confirm with the user before deleting.
- Instead of deleting, you can propose commenting it out or marking it "to be applied later".
