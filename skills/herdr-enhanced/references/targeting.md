# Targets and reference points

This is where herdr operations go wrong most often. The command itself succeeds, but **it lands on
the wrong pane.** The failure never surfaces as an error — it quietly rearranges someone else's
screen — so the person is usually the one who notices.

## "Here" is the pane the instruction arrived in, not the pane the person is looking at

"open a pane on the right", "put it beside this", "run it here" — the reference point for every one
of these is **the pane that received the instruction**. That holds even when the person is working
in another tab at this moment. They spoke **to you**; they did not point at whatever was on their
own screen.

herdr's pane commands fall back to **the UI-focused pane** when you omit the target. That pane may
be in active use by the person, or belong to another client entirely. An incident of exactly this
shape has happened: a session running in the background received "open it on the right", split the
active window, and the full-width window the person had been using became half-width.

So **not omitting the target is the default.**

```bash
printf '%s\n' "$HERDR_WORKSPACE_ID" "$HERDR_TAB_ID" "$HERDR_PANE_ID"
herdr pane current --current
```

Use `--current` when your own pane is the reference point. Pass another pane's ID **only when the
person named a different place.** When a tool does not know where it stands, the person's own eyes
have to fill that gap.

## Name the target as one of three things

| Situation | How to address it |
|---|---|
| The calling pane itself | `"$HERDR_PANE_ID"` — the **slot** it goes in differs per command (see below) |
| Another pane | The pane ID read out of a response (`w1:p3`) |
| A specific agent | A live, unique agent name |

**`--current` depends on the command.** The official skill says to prefer `--current` for pane
commands, but in practice it comes down to **how that command accepts its target** (measured).

| How the target is accepted | Commands | `--current` |
|---|---|---|
| Options only (`[OPTIONS]`) | `pane current`, `pane layout`, `pane edges`, `pane process-info`, `pane split` | works |
| Positional argument (`<PANE_ID>`) | `pane read`, `pane get`, `agent get`, `agent read` | **does not work** |

Used with the latter, `--current` is read as a pane-name string and you get
`{"error":{"code":"pane_not_found","message":"pane --current not found"}}`. Because the error says
"no such pane", **it is easy to misdiagnose as a wrong target** — the option is simply unsupported
there.

**`"$HERDR_PANE_ID"` has a fixed slot too.** The commands in the upper row accept **no positional
argument at all** (measured: `pane layout`'s usage line is `[OPTIONS]` only), so passing it bare
fails with a shell usage error rather than a JSON error. If you are expecting the earlier error
shape, you will not find the cause.

| How the target is accepted | How to point at your own pane |
|---|---|
| Options only | `--pane "$HERDR_PANE_ID"` or `--current` |
| Positional argument | `"$HERDR_PANE_ID"` |

When in doubt, read that command's `--help`. A `<PANE_ID>` in the usage line means positional;
`[OPTIONS]` alone means an option.

IDs are opaque, stable handles. **Read them out of JSON responses; never infer them from sidebar
order or from examples in documentation.** IDs of closed tabs and panes are not recycled, so a stale
ID will not point at someone else's pane — but a guessed ID may have been someone else's from the
start.

**Names are different — they are recycled.** A name follows the current occupant of a pane, and
when that agent ends or is replaced the name is released, so **another agent can take it over.**
This bites on long delegations: hold a reply address as a name, send to it twenty minutes later, and
the name may have changed hands in the meantime, **dropping your result into an unrelated session.**
Addresses you have to hold for a while should be pane IDs, or verify with `agent get` right before
you send that it is still the same target.

Move a pane to another workspace and **you get a new pane ID scoped to that workspace.** Read the
new ID out of the move response and carry on with it. The old ID resolves only within the caller
context the process inherited, so it must not be used as a general target.

## When resolution fails, stop — do not silently fall back

Ignoring the location a person specified and opening somewhere arbitrary **betrays the intent of
that specification.** This fallback has caused an incident where the person moved the pane by hand
afterwards: the skill handed its own job back to them.

- If you cannot pin down the target, **do nothing and say so.** Do not fill the gap with a guess.
- Do not fall back to an empty value or a default. **An empty target is not "no target" — it is read
  as "the current screen."**
- If several candidates fit, do not narrow it yourself; ask which one.

## Use names when speaking to people

`w1:p3` is **the most precise address a command argument can take**, so use it there. But translate
it to a name when you carry it back to a person. People remember by name, not by position or number.

```bash
herdr agent rename <target> reviewer
herdr pane rename <pane_id> "test runner"
```

Name what can be named, and refer to what is named by its name. When there is no name, **say that it
is unnamed**. Not `delegated to w1:p3` but `delegated to reviewer`, or `ran it in the unnamed pane
on the right (w1:p3)`.

## A pane you create belongs to that tab and does not follow you

Splitting a pane is **a judgment made at that instant about "the tab I am in right now."** The pane
that results belongs to that tab, and it does not follow your pane if yours is later moved to
another tab.

Here is an incident. Two agents were opened alongside, and then the person rearranged window order,
moving only your pane. The two agents stayed in the original window, whose first slot now held
someone else's session. To the person's eye, they had been parked in the wrong place. **The judgment
at placement time was correct and the rules were followed; the reference point moved afterwards** —
not the kind of thing you can prevent up front.

So check membership after opening several panes.

```bash
herdr pane list --workspace "$HERDR_WORKSPACE_ID"   # this workspace only — correct here, since membership is the point
herdr tab list --workspace "$HERDR_WORKSPACE_ID"
```

If a pane you just opened is not in your tab, it has drifted. Pull it back with the pane-move
command. Leave the layout wrong and the person moves it by hand — at which point there was no reason
to use this tool at all.
