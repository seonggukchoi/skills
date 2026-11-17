# Which way to split, and checking that it went that way

Layout is **changing the screen a person is looking at right now.** Get it wrong and a correction
comes straight back, and those round trips add up. Deciding before you act costs far less than
fixing after.

Settling the reference point first is covered in [targeting.md](targeting.md). This file covers which
direction to split and how to confirm it; opening several panes, sizes, and focus are in
[layout-arranging.md](layout-arranging.md).

How to carry it out:
[tui/splitting.md](../tui/splitting.md) (`--direction right|down`, splitting then swapping for left
or top, reading coordinates back with `pane layout`) ·
[app/layout.md](../app/layout.md) (`scripts/app/hc-layout open|place`, four directions, the
`verified` field).

## Translate what the person said into a direction

People describe **the picture they want to see**, and a split command takes **where the new pane
goes.** Those are not the same statement, so a translation step is required. Skip this table on the
grounds that "a direction was given, so use it" and layout phrasings like `side by side` never
register as a direction, dropping you into the shape rule below.

| What the person said | Layout to build | New pane goes |
|---|---|---|
| side by side, beside, next to, on the right, on the left, on either side | split on a vertical boundary and **lay them out across** | right (or left) |
| stacked, one above the other, below, on top, underneath | split on a horizontal boundary and **stack them down** | down (or up) |

Which direction values each CLI accepts differs: the herdr TUI splits only `right` and `down`, so
left and top need a swap afterwards ([tui/splitting.md](../tui/splitting.md)), while
`scripts/app/hc-layout` takes all four ([app/layout.md](../app/layout.md)). **A request for the left
or the top is a different screen from the right or the bottom**; leaving it on the right without
comment produces a screen other than the one requested.

## Do not pass "horizontal" and "vertical" through as-is

**These words mean opposite things across tools.** The same `horizontal` splits left/right in one
tool and top/bottom in another: tmux's `split-window -h` gives side-by-side panes, while several
terminal apps' "Split Horizontally" stacks them. Plain English is ambiguous on its own terms too —
"split it horizontally" reads either as *lay them out horizontally* (left/right) or as *cut along a
horizontal line* (top/bottom).

So when these words come in, **the direction is not settled — it is still open.**

- If context settles it (for example "horizontally side by side", or "split on a horizontal line,
  one above the other"), translate to the settled side.
- If it does not settle, **ask.** "Two side by side (left and right), or split on a horizontal line
  into top and bottom?" Asking once costs less than rebuilding a layout.
- Do not use these words when speaking back to the person either. **Say "left and right" or "top and
  bottom."**

## When there is an instruction, do not apply the shape rule

If the user stated a direction, **that settles it.** Do not check the pane's shape. Check it and the
rule offers an answer that differs from the instruction, and being more concrete, it pulls you that
way. herdr windows are usually wider than 250 columns, so the shape rule **points at "right" almost
every time.** That is why an instruction of "stacked" gets overturned here more than anywhere else.

Look at the target pane's shape, with the official skill's rule (wide panes right, narrow or tall
panes down), only when no direction was stated.

## Verify the layout after splitting

**A successful split response does not prove the direction.** In the TUI the `pane split` response
carries no coordinates at all (measured); give the wrong direction and the command still succeeds
with a normal response. **Nobody knows until a person looks at the screen and points it out.**

So read the layout back after splitting, and judge by **the relationship between the reference pane
and the new one:**

- **Placed left and right** — they sit side by side in the same row; the new one is after the
  reference for "right", before it for "left".
- **Placed top and bottom** — they sit stacked in the same column; the new one is after the
  reference for "down", before it for "up".

In the TUI that means coordinates from `pane layout` ([tui/splitting.md](../tui/splitting.md)); in hc
mode `hc-layout` reads the tree back itself and reports `verified`
([app/layout.md](../app/layout.md)).

If it came out wrong, **fix it before handing back to a person.** Close it and split again if it is
empty and yours; otherwise rearrange it ([tui/rearranging.md](../tui/rearranging.md) in the TUI,
`place` in hc mode).
