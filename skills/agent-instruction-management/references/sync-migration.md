# Sync Structure Migration Procedure

The procedure for migrating per-agent instruction files that are currently set up as **duplicate files** (separate, standalone content) or **symbolic links** to the standard structure: an `AGENTS.md` source plus `@` references.

> This migration is classified as a **significant edit** and always requires user approval. — A file-structure change affects how every agent loads its instructions, so a botched migration can leave an agent reading empty instructions.

---

## Migration Procedure

### 1. Assess the Current Structure

Assessing the type and content of the existing files before migrating allows a safe migration without losing content.

Check the instruction files at the project root:

- Identify whether each file is a **symbolic link**, a **regular file**, or an **`@` reference**.
- Read the file content to determine whether it is standalone content or a reference.

### 2. If Already in the Standard Structure

- If `AGENTS.md` is the source and other files are `@` references or unneeded → no migration needed. Done.

### 3. If a `@`-Supporting Agent's File Has Separate Content

e.g., `CLAUDE.md` has standalone content different from `AGENTS.md`.

1. **Compare** the content of `AGENTS.md` and the file in question.
2. If they differ:
   - Check each file's last-modified time in version control.
   - **Merge** into `AGENTS.md`, using the most recently modified content as the baseline.
   - Ensure content unique to one of the two files is not lost. — Dropping a rule that exists in only one file makes it disappear after migration.
   - Get the user to **confirm** the merged content.
3. Replace that file with an `@` reference.

### 4. If It Is a Symbolic Link

- **Delete** the symbolic link and replace it with an `@`-reference file. — Symlinks can break depending on OS/Git settings, so `@` references are more stable.
- If the symlink's target file content differs from `AGENTS.md`, follow the merge procedure in Step 3.

### 5. Execute Migration for `@`-Supporting Agents

Delete that agent's workspace instruction file and replace it with a file containing only the single line `@./AGENTS.md`.

Example (for CLAUDE.md):
- Delete the existing `CLAUDE.md`
- Write the single line `@./AGENTS.md` in the new `CLAUDE.md`

### 6. Agents Without `@` Support

- **Codex**: reads `AGENTS.md` directly, so no special handling is needed.
- **Gemini**: copy the `AGENTS.md` content into `GEMINI.md` and add a sync comment at the top:

```markdown
<!-- This file is synced from AGENTS.md. Do not edit it directly. -->
```

### 7. Verify

After migration, verify that every agent reads the correct instructions.

- Verify each `@`-reference file contains **only one line**.
- Verify the synced files' content matches `AGENTS.md`.
- Verify no existing content was lost in the migration.

---

## Cautions

- **Always** assess the current structure first so existing file content is not lost. — Overwriting without checking can erase rules that were managed independently.
- An `@`-reference file contains only the one reference line. Do not add other content. — Mixing the reference with standalone content makes it unpredictable which one the agent follows.
- **Do not apply this migration procedure at the global level.** Global instructions are managed independently per agent. — Each agent has a different global path and parsing method, so consolidation is impossible.
- If content must be merged during migration, always have the user confirm the merged result.
