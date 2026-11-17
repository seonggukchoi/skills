# Several panes, ratios, and sizes with the herdr CLI

Even shares by default, not stacking in one direction, opening everything before tidying, offering
candidates for an ambiguous instruction, keeping focus, and reporting what cannot be built are in
[common/layout-arranging.md](../common/layout-arranging.md). This file is the herdr arithmetic and
commands.

## Equal panes: `--ratio` is the share the original keeps

`--ratio` is **the share the original pane keeps** (measured). To build n equal columns, give the
original `1/n`, then `1/(n-1)`, and so on. Since the remaining space shrinks with every split, **that
share grows with each round** — for three it is 0.33 then 0.5; for four, 0.25 · 0.33 · 0.5. Start
from 0.5 instead and the first column takes half, with each later one narrower (measured without
ratios: widths 129 · 64 · 64).

```bash
# three equal columns — measured widths 85 · 86 · 86
A=$(herdr pane split --current --direction right --ratio 0.33 --cwd "$PWD" --no-focus \
    | python3 -c 'import sys, json; print(json.load(sys.stdin)["result"]["pane"]["pane_id"])')
herdr pane split --pane "$A" --direction right --ratio 0.5 --cwd "$PWD" --no-focus
```

```bash
# three equal rows — the same procedure with --direction down (not measured; verify with pane layout)
A=$(herdr pane split --current --direction down --ratio 0.33 --cwd "$PWD" --no-focus \
    | python3 -c 'import sys, json; print(json.load(sys.stdin)["result"]["pane"]["pane_id"])')
herdr pane split --pane "$A" --direction down --ratio 0.5 --cwd "$PWD" --no-focus
```

You can also keep using the original as the reference, but new panes then wedge in beside the
original one after another and **the order reverses.** When the person will refer to them as "the
first, the second", build them the way shown above and attach names with `pane rename`.

## The direction of a resize means something else than the direction of a split

`split --direction` is **where the new pane goes**, but `resize --direction` means **push that
boundary of the target pane in that direction.** The same argument name points at different things.

So **passing the opposite direction does not undo it.** In three columns, giving `left` to the middle
pane moves its left boundary, and giving `right` to the same pane moves its right boundary. Those are
different boundaries, so chaining the two skews the layout further (measured: each changed a
different split's ratio).

- `--amount` is not a column count but **a change in ratio.** `0.1` moves that split's ratio by 0.1.
- If you intend to undo, **write down the `ratio` from `pane layout`'s `splits` before changing it**
  and restore that value.
- When all you need is one pane bigger, do not touch sizes — zoom instead. It is far easier to undo.

```bash
herdr pane zoom <pane_id> --toggle
```

## Alerting without moving focus

Background work keeps `--no-focus` (the official skill's safety rules). When the situation calls for
an alert, raise a notification instead of moving the screen.

```bash
herdr notification show "tests finished" --body "results are in the reviewer pane" --sound done
```

## What the herdr TUI cannot express

- **Arranging a grid in one step.** Stacking splits one at a time is the only way, which is why
  ratios are set at creation.
- **Splitting directly to the left or upward.** You have to split and then swap
  ([splitting.md](splitting.md)).
- **Flipping a split's direction after the fact.** Turning a left/right pair into top/bottom means
  moving panes or rebuilding them.
- **Moving a pane within its own tab in one step.** It takes the two-step move through a temporary
  tab ([rearranging.md](rearranging.md)); that procedure is the supported route, not a way around
  this list.

Report these as [common/layout-arranging.md](../common/layout-arranging.md) describes rather than
forcing them.
