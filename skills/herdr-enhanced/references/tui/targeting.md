# Naming targets with the herdr CLI

The principles — "here" is the pane the instruction arrived in, never omit the target, stop when it
cannot be resolved, names to people, panes stay in the tab they were made in — are in
[common/targeting.md](../common/targeting.md). This file is how to carry them out with `herdr`.

## Never omit the target

Omit the target and most herdr commands fall back to **the UI-focused pane.** (The official skill says
an omitted `pane split` target now uses the calling pane when `HERDR_PANE_ID` is set, but other
commands may still take the focused pane, so the rule does not change.)

Know where you stand first.

```bash
printf '%s\n' "$HERDR_WORKSPACE_ID" "$HERDR_TAB_ID" "$HERDR_PANE_ID"
herdr pane current --current
```

Use `--current` (where the command accepts it, below) when your own pane is the reference point.
Pass another pane's ID only when the person named a different place.

Name the target as one of three things.

| Situation | How to address it |
|---|---|
| The calling pane itself | `"$HERDR_PANE_ID"` — the **slot** it goes in differs per command (see below) |
| Another pane | The pane ID read out of a response (`w1:p3`) |
| A specific agent | A live, unique agent name |

## `--current` and `$HERDR_PANE_ID` depend on the command

The official skill says to prefer `--current` for pane commands, but in practice it comes down to
**how that command accepts its target** (measured).

| How the target is accepted | Commands | `--current` |
|---|---|---|
| Options only (`[OPTIONS]`) | `pane current`, `pane layout`, `pane edges`, `pane process-info` | works |
| Either (`[PANE_ID]` or an option) | `pane split`, `pane zoom` | works |
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
| Either | any of the three |
| Positional argument | `"$HERDR_PANE_ID"` |

When in doubt, read that command's `--help`. A `<PANE_ID>` in the usage line means positional;
`[OPTIONS]` alone means an option.

## IDs and names

How IDs and names behave (read from JSON, not reused, renumbered by a workspace move; names follow
the pane's occupant) is in the official skill's "Use IDs and caller context". Hold a long-lived
address as a pane ID; if you must send to a name a while later, check with `agent get` right before
sending that it is still the same target.

Name what you create so people can refer to it.

```bash
herdr agent rename <target> reviewer
herdr pane rename <pane_id> "test runner"
```

## Check membership

After opening several panes, confirm they are in your tab.

```bash
herdr pane list --workspace "$HERDR_WORKSPACE_ID"   # this workspace only — correct here, since membership is the point
herdr tab list --workspace "$HERDR_WORKSPACE_ID"
```

If a pane you just opened is not in your tab, it has drifted. Pull it back with
`pane move <pane> --tab <your tab> --split right|down --target-pane <pane beside it> --no-focus`.
This works because the pane is in another tab; a move aimed at the tab the pane is already in does
nothing and still exits 0 (measured). For rearranging inside one tab, see
[rearranging.md](rearranging.md).
