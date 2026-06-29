# Instruction Rule-Writing Examples

A collection of good-vs-bad rule comparisons and rule-writing examples across various domains. Refer to this when writing new instruction rules or improving existing ones.

---

## Core Principles

1. **Clear action directives**: describe concrete actions instead of vague adjectives. — An agent cannot define "well" or "appropriately".
2. **Include the reason**: explain in one sentence why the rule is needed. — An agent that knows the reason judges correctly even in edge cases.
3. **Concrete examples**: include real applications such as code, commands, or file paths. — Examples reduce interpretation variance for abstract rules.
4. **Remove forbidden wording**: do not use vague modifiers such as "if possible", "preferably", "well", or "appropriately". — Vague wording weakens a rule's enforceability.

---

## Bad Rule vs. Good Rule Comparison

### Example 1: Testing

**Bad** (vague, no reason):

```markdown
- Write tests well
```

**Good** (clear, with reason and example):

```markdown
- Write a test case for each public method/function.
  - Reason: catches regression bugs early during refactoring.
- Cover both normal and exceptional cases.
- Test names state the subject under test and the expected result.
  - Example: `'returns InvalidAmountError when the payment amount is 0'`
  - Bad example: `'test1'`, `'payment test'`
```

### Example 2: Error Handling

**Bad**:

```markdown
- Handle errors appropriately
```

**Good**:

```markdown
- Wrap external API calls in try-catch and, on failure, return an error that includes the cause.
  - Reason: showing only "request failed" without the cause makes debugging hard.
  - Example:
    ```typescript
    try {
      const result = await fetch(url);
      if (!result.ok) {
        throw new ApiError(`HTTP ${result.status}: ${url}`);
      }
    } catch (error) {
      throw new ApiError(`${url} call failed: ${error.message}`);
    }
    ```
```

### Example 3: Explicit Types

**Bad**:

```markdown
- Specify types if possible
```

**Good**:

```markdown
- Specify types for all function parameters and return values.
  - Reason: relying on type inference can hide unintended type changes during refactoring.
  - Example:
    ```typescript
    // Bad
    function calculate(amount, rate) { ... }

    // Good
    function calculate(amount: number, rate: number): number { ... }
    ```
```

### Example 4: Git Commit Messages

**Bad**:

```markdown
- Write good commit messages
```

**Good**:

```markdown
- Commit messages follow the Conventional Commits format: `{type}({scope}): {description}`
  - type: one of `feat`, `fix`, `refactor`, `docs`, `test`, `chore`
  - scope: the module being changed (e.g., `auth`, `payment`, `ui`)
  - description: English, present tense, ≤50 characters
  - Example: `feat(auth): add Google social login`
  - Bad example: `update`, `fix bug`, `update code`
```

### Example 5: Environment Variables

**Bad**:

```markdown
- Manage environment variables appropriately
```

**Good**:

```markdown
- Document each environment variable's key name and description in `.env.example`. Do not include actual values.
  - Reason: `.env` is not committed to Git, so new teammates need a way to discover the required environment variables.
  - Example:
    ```env
    # .env.example
    DATABASE_URL=         # PostgreSQL connection string
    REDIS_URL=            # Redis cache server URL
    JWT_SECRET=           # JWT token signing key (min. 32 chars)
    ```
```

---

## Rule-Writing Patterns by Domain

### Build/Run Commands

```markdown
## Build & Run

- Dev server: `pnpm dev` (port 3000)
- Production build: `pnpm build`
- Run all tests: `pnpm test`
- Test a specific file: `pnpm test -- {file-path}`
- Lint check: `pnpm lint`
```

### Project Structure Rules

```markdown
## Project Structure

- New page: create `index.tsx` and `styles.ts` in `src/pages/{page-name}/`
- Shared components: place under `src/components/`
- API call functions: split into per-domain files under `src/api/`
  - Example: `src/api/auth.ts`, `src/api/payment.ts`
- Type definitions: split into `types.ts` in the same directory as the module
```

### Prohibition Pattern

**Always state the reason** alongside each prohibition. A prohibition without a reason leaves the agent unable to apply it correctly in analogous situations, where it may either circumvent or over-apply the rule.

```markdown
## Prohibitions

- Using the `any` type is **strictly prohibited**. Use `unknown` and narrow with type guards.
  - Reason: `any` disables type checking and becomes a source of runtime errors.
- Do not leave `console.log` in production code. Use the `logger` module when logging is needed.
  - Reason: `console.log` is unstructured, making log collection/search impossible.
- Do not specify route paths with hardcoded strings. Use the `ROUTES` constant object.
  - Reason: when a path changes, every hardcoded string must be found and updated, creating a high risk of omission.
  - Example:
    ```typescript
    // Prohibited
    navigate('/users/profile');

    // Allowed
    navigate(ROUTES.USER.PROFILE);
    ```
```

---

## Rule-Writing Checklist

| #   | Item                                               |
| --- | -------------------------------------------------- |
| 1   | Does it specify a concrete action? (verb + object) |
| 2   | Is the reason explained in one sentence?           |
| 3   | Does it include a concrete example (code, command, path)? |
| 4   | Is it free of vague wording (e.g., "appropriately", "if possible")? |
| 5   | Does it contrast a bad example with a good one?    |
| 6   | Is it written in an imperative/directive tone?     |
