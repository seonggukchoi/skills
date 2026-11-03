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

### hc mode

Entries carrying `"mode": "hc"` (trigger queries 24 to 29, behavioral scenarios 15 to 18) are for
the herdr app's `hc` CLI. Run them inside a terminal started by `hc`, where `$HC_TERMINAL_ID` is set
and the herdr TUI variables are not. Run the two groups separately; each fails in the other's
environment, and that is correct behavior.

**Use an isolated hc core**, as `hc_environment` in `evals.json` describes: its own `HC_SESSION`,
scratch XDG paths, and the inherited `HC_TERMINAL_*` variables removed. `hc ls` lists every live
terminal and `hc send` reaches any of them, so a subject in the default core can touch real work.
Never stop or restart the default core.

**Isolate the core, not the agent.** Every terminal the core starts inherits the core's environment,
not that of the `hc run` caller (measured), so a subject started plainly sees the scratch XDG paths.
An agent and its plugins resolve their own data and config directories from those variables, and
can write the scratch path back into the agent's real configuration, which the XDG variables do not
move. Once the scratch directories are removed, the person's real setup points at nothing. So start
the subject through a launcher that restores the XDG values from before the core started, and
unsets the ones that were unset. Do not isolate the agent's own config directory instead: that cuts
off its login, plugins, and installed skills, and the run no longer measures the real setup.

The subject's own `hc` still reaches the isolated core, because the core puts `HC_TERMINAL_SOCKET`
and `HC_SESSION` into each terminal it starts (measured).

Build the wrapper and the launcher once, from the shell that runs the evaluation, before the core
starts. The launcher also pins `PATH`, since the core passes on whatever `PATH` started it. And it
unsets `CLAUDE_CODE_CHILD_SESSION`: a core started from inside a Claude Code session passes that
marker on, and a subject that inherits it does not save its transcript (measured), which is the
execution record grading reads.

```sh
eval_root=$(mktemp -d)
mkdir -p "$eval_root/bin" "$eval_root/config" "$eval_root/data" "$eval_root/state" "$eval_root/cache"
real_hc=$(command -v hc)

# hc-eval: hc against the isolated core. The scratch XDG paths reach the core and nothing else.
cat > "$eval_root/bin/hc-eval" <<EOF
#!/bin/sh
exec env -u HC_TERMINAL_ID -u HC_TERMINAL_SOCKET -u HC_SCOPE HC_SESSION=herdr-eval \\
  XDG_CONFIG_HOME="$eval_root/config" XDG_DATA_HOME="$eval_root/data" \\
  XDG_STATE_HOME="$eval_root/state" XDG_CACHE_HOME="$eval_root/cache" "$real_hc" "\$@"
EOF

# eval-agent: starts the subject with this shell's XDG values and PATH, not the core's,
# and without a parent session's marker that turns off transcript saving.
{
  echo '#!/bin/sh'
  for var_name in XDG_CONFIG_HOME XDG_DATA_HOME XDG_STATE_HOME XDG_CACHE_HOME PATH; do
    if var_value=$(printenv "$var_name"); then
      printf "export %s='%s'\n" "$var_name" "$(printf '%s' "$var_value" | sed "s/'/'\\\\''/g")"
    else
      printf 'unset %s\n' "$var_name"
    fi
  done
  echo 'unset CLAUDE_CODE_CHILD_SESSION'
  echo 'exec claude "$@"'
} > "$eval_root/bin/eval-agent"
chmod +x "$eval_root/bin/hc-eval" "$eval_root/bin/eval-agent"

# Start the core before exporting, so the two paths stay out of the subjects' environment.
"$eval_root/bin/hc-eval" server start
export HC_EVAL_BIN="$eval_root/bin/hc-eval" HC_EVAL_AGENT="$eval_root/bin/eval-agent"
```

The scenarios' `setup_script` start every agent as `"$HC_EVAL_BIN" run ... "$HC_EVAL_AGENT"`. After
the whole run, `"$HC_EVAL_BIN" server stop` and remove `$eval_root`.

The baseline for hc mode is this skill hidden with only `hc --skill` available.

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
