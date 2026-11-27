# Arranging panes in hc mode: `scripts/app/hc-layout`

Which direction the person meant and verifying it are in
[common/layout-direction.md](../common/layout-direction.md); several panes, sizes, focus, and
reporting what cannot be built are in [common/layout-arranging.md](../common/layout-arranging.md).
This file is how to carry them out in hc mode.

hc runs terminals; it does not arrange windows. **`scripts/app/hc-layout` does every arrangement this
skill needs, from any machine, without moving focus.** Use it instead of rebuilding the steps. It
lives in this skill's own directory (the base directory shown when the skill loads), wherever the
skill was installed. How it reaches the layout — the app's commands or the layout document — is in
[layout-routes.md](layout-routes.md).

## Commands

```bash
L=<this skill's directory>/scripts/app/hc-layout
"$L" tree [space|tab|terminal ...] [--on M]       # the split tree: groups, direction, weights, ids
"$L" where "$HC_TERMINAL_ID"                       # the space, tab and pane holding a terminal
"$L" open --anchor <pane|terminal> --direction right|down|left|up [--ratio 6:4] [--cwd D] [-- CMD]
"$L" open --new-tab-in <space> [--name N] [--cwd D] [-- CMD]   # default CMD: the machine's shell
"$L" place <terminal> --anchor <pane|terminal> --direction D [--ratio A:B]  # running terminal there
"$L" resize <pane|terminal|group> --ratio 2:1[:1]  # that node and its siblings, in tree order
"$L" move-tab <tab> --to-space <space> [--index N] # same machine; tree, ids and sizes kept
"$L" adopt <terminal> --tab-of <terminal>          # add a running terminal at the end of a tab
```

- Read ids from `tree` or `herdr-app ls`; another machine's ids carry a `machine/` prefix in the app,
  and the script takes either form.
- **`--direction` takes all four directions.** Translate the person's words first
  ([common/layout-direction.md](../common/layout-direction.md)); left and up need no extra step here.
- `--ratio` on `open`/`place` is anchor:new and splits the share the two held, so other siblings keep
  theirs. For several equal panes, open them all, then set the whole split once with `resize`
  (`--ratio 1:1:1`).
- Every command prints JSON with the route it took (`via`); `place` and `open` also report
  `verified` from reading the tree back. **Read `verified`**: `false` means the tree does not show the
  pane where asked; check with `tree` and fix it before handing back to a person.
- **A failed `place` or `move-tab` stops partway.** Its placeholders are removed, but a terminal it
  had already labelled lands at the end of the tab's outermost split, and `move-tab` leaves the tab
  split between the two spaces (measured). Read `tree`, then finish with `place` or `resize`.
- Find your own place with `where "$HC_TERMINAL_ID"`, and check membership after opening several
  with `tree` ([common/targeting.md](../common/targeting.md)).

## Limits that hold on either route

- **A terminal belongs to its machine.** No tab or pane moves between machines; the script refuses.
- **Labels place only a terminal without a pane.** Relabelling a pane's terminal moves nothing
  (measured); moving one is `place` or `move-tab`.
- A labelled terminal with no app running and no `doc` write appears only when an app next starts.
  `hc run --bg --keep --label herdr.space=<id> --label herdr.tab=<id>` lands at the end of the
  tab's outermost split; with `herdr.space` only, as a new tab; with no labels, nowhere.
- A tab that is not shown reports default terminal sizes (120x40); judge sizes from `tree`.
- Weights are relative within one split; a missing weight counts as `1` (consistent with every
  measurement).

Anything beyond these, report as [common/layout-arranging.md](../common/layout-arranging.md)
describes rather than working around it.

Terminals `open` starts, and the placeholders the script removes, are covered in
[lifecycle.md](lifecycle.md).
