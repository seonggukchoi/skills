# herdr-enhanced evaluations

This skill fails at two layers. Each layer asks a different question, so the sets are split.

| File | What it asks | What failure looks like |
|---|---|---|
| `trigger-evals.json` | **Does it load when it should** | Nothing happens. Only the official herdr skill loads, operations follow the syntax correctly, and an incident occurs with the judgment rules missing |
| `evals.json` | **Does it follow the rules once loaded** | The commands succeed and the answer sounds plausible, but the result is wrong |

Both layers **fail silently.** No error is raised, so without automated regression there is no way to
notice.

## Why trigger behavior is measured separately

This skill and the official `herdr` skill **divide labor rather than compete.** That one holds CLI
syntax, this one holds judgment, so when operating herdr **both loading is the correct outcome.**
Their names overlap, though, which makes it easy for only one to load — and the one left out is
usually this skill. So the first axis of `trigger-evals.json` is "does it load alongside, in
situations where the official herdr skill loads."

The second axis is **requests where the word herdr never appears.** People say "open a pane on the
right" or "put it beside this"; they do not call the tool by name. The official herdr skill requires
an explicit mention, so that whole band is empty, and filling it is why this skill exists.

The third axis is **receiving a tag.** Receive a message beginning with an angle-bracket `herdr` tag
without loading, and you work without knowing how to reply, and the result simply disappears. The
requester waits forever.

The criterion is one line — **in a herdr environment, a request about the screen, panes, or agents
loads it; anything else does not.** Even when the user names a different tool, if herdr owns this
screen then this skill is the one that judges.

Negative cases are all near-misses: a one-shot investigation a subagent handles fine, an editor
split, a plain git worktree — **things that overlap in keyword or concept but have nothing to do with
herdr.** Obviously unrelated queries verify nothing, so they were left out.

## How to run it

### Prerequisites

herdr must be installed — <https://herdr.dev>. With Homebrew that is `brew install herdr`.

Get the official `herdr` skill too, to use as the baseline.

```bash
herdr --version
npx skills add https://github.com/herdrdev/herdr --skill herdr
```

### Trigger evaluation

**Run it inside herdr.** The `description` presumes `HERDR_ENV` and `$HERDR_PANE_ID`, so running it
outside herdr makes every positive case fail — that is **correct behavior**, and the result must not
be read as a regression.

```bash
printf '%s\n' "$HERDR_ENV" "$HERDR_PANE_ID"     # at least one must have a value
```

Use the skill-creator skill's description-optimization procedure as-is. Convert the `queries` array
into `[{"query": ..., "should_trigger": ...}]` form and hand it over.

```bash
python3 -c '
import json
d = json.load(open("evals/trigger-evals.json", encoding="utf-8"))
out = [{"query": q["query"], "should_trigger": q["should_trigger"]} for q in d["queries"]]
json.dump(out, open("/tmp/herdr-enhanced-trigger.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
'
```

Run each query several times and look at the trigger rate. A single result is too noisy to judge on.

### Behavioral evaluation

**Run it in an isolated session.** The evaluation genuinely creates and destroys panes, so running it
in a session a person is using touches their screen.

```bash
# a person launches this directly from a separate terminal
herdr --session herdr-enhanced-eval

# after the evaluation — attempt delete even if stop fails (with `&&` a stale session is left behind)
herdr session stop herdr-enhanced-eval; herdr session delete herdr-enhanced-eval
```

**A person has to create the isolation.** The first line above launches a TUI and attaches to it, so
an agent running the evaluation that calls it through Bash hangs right there. On top of that, the
agent runs inside a pane of the outer session, so the CLI points at the outer socket — `pane split`
and `close` **go straight out onto the screen the person is watching.** An agent cannot create its own
isolation.

For each scenario, run `setup_script` **as one whole shell** to build the conditions, then hand over
`prompt` verbatim and have the answer and **the execution record** captured. The `setup` field
describes why those conditions are needed; what actually builds them is `setup_script`.

**Do not split it up and run it line by line.** Variables and loops get severed, commands go out with
an empty target, and an empty target is read not as "no target" but as **the focused pane.** The
evaluation then touches the person's screen.

**Run `environment.teardown_script` after every single scenario.** Otherwise panes split by an earlier
scenario break the premises of a later one (scenario 9 requires that pane to occupy the whole tab),
and live agent names collide so that **from the second round onward every `agent start` fails.** That
failure looks like a regression in the skill but is a problem in the harness.

**Scenarios carrying `setup_manual` cannot be set up by commands alone.** Putting a pane's working
directory at home (2), pointing the reply address at a real pane (5), producing a `blocked` state (8),
and an environment where terminal-app variables are inherited (11) are those cases. Run them without
following that guidance and the scenario measures something other than what was intended.

Grading uses the `skill-creator` skill's procedure — `agents/grader.md`,
`scripts/aggregate_benchmark.py`, and `eval-viewer/generate_review.py` inside that skill's directory.

**Grade on the final answer alone and everything looks like a pass.** This skill's failures happen
after the command succeeds, so you have to check the execution record for which target was passed,
which options were attached, and what was verified before executing. The `assertions` are written
against that record.

### The baseline

Use **the state with only the official `herdr` skill loaded** as the baseline. The point is to see
where the two skills' roles divide, so "no skill" is not a meaningful comparison. Compare against a
state that does not know the herdr CLI at all and this skill's contribution looks larger than it is.

## Where results go

Run output stays outside the repository. Volume accumulates per round, and absolute paths from the
execution environment go in verbatim.

## Reading the results

Pass rates do not read at face value. These came out of actual rounds.

**Not really building the setup measures something else.** Describe the situation in the prompt
without launching an isolated session and you get a scenario at odds with real herdr state. The
receiving side prioritizes query results over description, and that judgment is itself correct, so it
looks like a pass while **a path other than the intended condition gets verified.** That is why
`setup_script` and `setup_manual` exist.

**Judging completion with `agent prompt --wait` cuts off mid-flight.** That option returns at the
first idle state, and when the screen empties while a coding agent calls a tool, herdr reads that as
`idle`. So an answer still mid-work gets graded as final, and several scenarios really were cut off at
"let me check." Judge completion either by watching `agent get` hold a state for a while, or by
whether the execution record's last tool call has finished.

**Some scenarios do not finish in one prompt.** When the grounds for a judgment are missing, the
receiving side asking back and stopping is correct, and for some items that is the right answer (6 and
10). But items where the actual operation has to be observed need that question answered to proceed.
When revising the set, decide whether to put the grounds in the prompt up front or to include a
follow-up answer alongside.

**Self-reporting is biased upward.** Instructing "list every tool you used" makes that instruction
itself raise awareness of the skill. Checking the first tool call directly in the transcript is more
accurate. If the execution path has no access to that record, state this bias whenever you quote the
numbers.

**Without a baseline you cannot state an improvement.** Without comparing against the state with only
the official herdr skill loaded, a high pass rate does not separate this skill's contribution from the
model's own baseline ability. Comparing means hiding this skill temporarily, which has the side effect
of changing the skill list mid-session, so a separate round is the better arrangement.

**When something does not line up, check whether the set is right before fixing the skill.** Run
results have caught errors in the set: two negative cases had been classified without folding the
herdr-environment premise into the judgment, which surfaced only on execution and was reversed.

## Revising the set

- **Do not make negative cases easy.** A query that is not a near-miss verifies nothing.
- **Do not strip the word herdr out of every positive case.** The explicit-mention band is where you
  check that it loads alongside the official herdr skill, so it is needed on its own.
- **Write `setup` alongside any new behavioral scenario.** Without reproducible conditions, that
  evaluation measures something different every round.
