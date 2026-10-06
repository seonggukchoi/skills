# Splitting and arranging the screen

Layout is **changing the screen a person is looking at right now.** Get it wrong and a correction
comes straight back, and those round trips add up. Deciding before you act costs far less than
fixing after.

Settling the reference point first is covered in `targeting.md`. This file covers which direction,
how many, and in what order to split.

## Translate what the person said into arguments

People describe **the picture they want to see**, and the CLI takes **where the new pane goes.**
Those are not the same statement, so a translation step is required. Skip this table on the grounds
that "a direction was given, so use it" and layout phrasings like `side by side` never register as a
direction, dropping you into the shape rule below.

| What the person said | Layout to build | `--direction` |
|---|---|---|
| side by side, beside, next to, on the right, on the left, on either side | split on a vertical boundary and **lay them out across** | `right` |
| stacked, one above the other, below, on top, underneath | split on a horizontal boundary and **stack them down** | `down` |

`--direction` accepts **only two values, `right` and `down`.** There is no `left`, `up`,
`horizontal`, or `vertical`. A request to put something on the left or on top cannot be passed
through directly, so use the workaround in the next section.

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
way. herdr windows are usually wider than 250 columns, so the shape rule **points at `right` almost
every time.** That is why an instruction of "stacked" gets overturned here more than anywhere else.

Look at the target pane's shape only when no direction was stated.

```bash
herdr pane layout --pane "$HERDR_PANE_ID"
```

- **Wide panes split to the right** — `--direction right`
- **Narrow or tall panes split downward** — `--direction down`

## Left and top mean splitting first, then swapping

`pane split` creates a new pane **only to the right or below.** When a person says "open it on the
left", split right and then swap the two panes with `pane swap`. Leaving it on the right without
comment produces a screen other than the one requested.

```bash
NEW=$(herdr pane split --current --direction right --cwd "$PWD" --no-focus \
      | python3 -c 'import sys, json; print(json.load(sys.stdin)["result"]["pane"]["pane_id"])')
[ -n "$NEW" ] || { echo "split failed — not swapping" >&2; exit 1; }
herdr pane swap --source-pane "$HERDR_PANE_ID" --target-pane "$NEW"
```

**Do not drop the empty check.** herdr writes errors to stderr and exits 1, so a failed split leaves
`python3` with empty input and `NEW` silently an empty string. Pass that through as
`--target-pane ""` and **an empty target is not "no target" — it is read as "the current screen"**
(`targeting.md`), swapping places with the pane the person was watching. This is where this
document's own example would cause the incident this document exists to prevent.

A request for the top works the same way — split `down`, then swap. **Swapping moves your own pane.**
The place the person was looking at changes, so say in your report that you swapped. Focus also goes
to the source pane — here your own — and herdr shows that tab (measured), so this pattern fits only
when your pane is the one on screen. The details are in "Rearranging panes inside one tab" below.

`pane neighbor`, `focus`, `resize`, and `swap` all take four directions. That makes direction
arguments look universal, but **only the splitting command is limited to two.**

## Verify the layout after splitting

**The `pane split` response carries no coordinates** (measured). What comes back is `pane_id`,
`cwd`, and `tab_id`, so that response alone cannot tell you whether the new pane appeared to the
right or below. Give the wrong direction and the command still succeeds with a normal response.
**Nobody knows until a person looks at the screen and points it out.**

So read the coordinates separately after splitting.

```bash
herdr pane layout --pane "$HERDR_PANE_ID" | python3 -c '
import sys, json
d = json.load(sys.stdin)["result"]["layout"]
for p in sorted(d["panes"], key=lambda q: (q["rect"]["y"], q["rect"]["x"])):
    r = p["rect"]
    print(p["pane_id"], "x=%d y=%d w=%d h=%d" % (r["x"], r["y"], r["width"], r["height"]))
'
```

The criterion is **the coordinate relationship between the reference pane and the new one.**

- **Placed left and right** — `x` differs, `y` matches. The new pane has the larger `x`.
- **Placed top and bottom** — `y` differs, `x` matches. The new pane has the larger `y`.

The same response's `splits` array carries each split's `direction` and `ratio` directly. With
several panes, that is the easier read.

If it came out wrong, **fix it before handing back to a person.** Close it and split again if it is
empty; otherwise rearrange it inside the tab as the next section describes. `pane move --tab` aimed
at the tab the pane is already in does nothing.

## Rearranging panes inside one tab

**`pane move` into the pane's own tab is a no-op that reports success** (measured). With or without
`--target-pane`, it exits 0 and the layout stays exactly as it was. The only trace is in the
response:

```
"move_result": {"changed": false, "reason": "same_tab", ...}
```

So never use it for same-tab moves, and **read `changed` in every `pane move` and `pane swap`
response** — a `false` there is the whole error report. This is the trap that sent several sessions
off moving panes through a temporary tab by improvisation.

Two operations do rearrange a tab, and they keep and change different things (all measured).

| | `pane swap` | Move out to a temporary tab, then back |
|---|---|---|
| What changes | Only **which pane sits in which slot.** The split tree (directions, ratios) stays as it was | The **shape.** The pane leaves its slot (its sibling takes the space) and comes back as a new split next to `--target-pane` |
| Pane IDs, agent names | Kept | Kept — the pane stays in the same workspace, so its ID does not change |
| Focus | **Moves to the source pane**, and herdr **switches the screen to that tab and workspace** even if the person was looking elsewhere. There is no `--no-focus` | Unchanged with `--no-focus` — **unless the moved pane was the focused one in its tab:** focus then passes to another pane and does not come back |
| Leftovers | None | The temporary tab **closes itself** once its only pane leaves |

`pane swap --direction` with no pane on that side also exits 0 with `"changed": false` and
`"reason": "no_neighbor"`.

Choose by what the result should look like.

1. **Two panes trade places and the shape stays** → `pane swap --source-pane --target-pane`. Make
   the source **the pane that has focus in that tab**, if it is one of the two; then focus stays on
   the same pane. Swap only in the tab the person is looking at, since a swap elsewhere pulls their
   screen there — for a tab out of view, use the two-step move even for a plain exchange.
2. **The shape changes** (a column becomes a stack, a pane joins another column, a split flips
   direction) → the two-step move below. Swap cannot change shape, and the same-tab move does
   nothing.

The two-step move is the documented procedure, not a workaround. Run it with `--no-focus` on both
steps, check `changed` on each, and confirm the temporary tab is gone.

```bash
pane_to_move=<pane id>      # the pane to move
anchor_pane=<pane id>       # the pane in the same tab it should sit beside
side=down                   # where it goes relative to the anchor: right or down

pane_info=$(herdr pane get "$pane_to_move" \
  | python3 -c 'import sys, json; p = json.load(sys.stdin)["result"]["pane"]; print(p["tab_id"], p["workspace_id"])')
home_tab=${pane_info% *}
home_workspace=${pane_info#* }
[ -n "$home_tab" ] || { echo "could not read the pane; nothing moved" >&2; exit 1; }

# 1) Out to a temporary tab that holds only this pane.
temp_tab=$(herdr pane move "$pane_to_move" --new-tab --workspace "$home_workspace" --label tmp-move --no-focus \
  | python3 -c 'import sys, json; m = json.load(sys.stdin)["result"]["move_result"]; print(m["pane"]["tab_id"] if m["changed"] else "")')
[ -n "$temp_tab" ] || { echo "step 1 did not move the pane; nothing changed" >&2; exit 1; }

# 2) Back into the original tab, beside the anchor.
landed_tab=$(herdr pane move "$pane_to_move" --tab "$home_tab" --split "$side" --target-pane "$anchor_pane" --no-focus \
  | python3 -c 'import sys, json; m = json.load(sys.stdin)["result"]["move_result"]; print(m["pane"]["tab_id"] if m["changed"] else "")')
[ "$landed_tab" = "$home_tab" ] \
  || { echo "step 2 failed: the pane is still in $temp_tab — bring it back before anything else" >&2; exit 1; }

# 3) The temporary tab should have closed itself. Confirm it is gone.
herdr tab get "$temp_tab" >/dev/null 2>&1 && echo "temporary tab $temp_tab is still open — close it" >&2
```

**A temporary tab must not outlive the procedure.** If step 2 fails, the pane is stranded in a tab
the person never asked for; move it back (or report where it is) before doing anything else. Use
`--new-tab` rather than `tab create` for step 1 — a tab from `tab create` comes with its own shell
pane, so it stays open after the move and you would have to close it yourself.

Then verify with `pane layout` as in the section above. `--ratio` on step 2 is the share the anchor
keeps, the same as in a split (measured: `--ratio 0.25` beside a 120-column anchor left it 30 wide).

## When creating several, fix the reference pane and the ratios up front

**Unless the person states a ratio, divide as evenly as possible** — every pane gets the same share
by default, and the steps below are how to get there.

Even with the right direction, **which pane you split for the nth one** changes the picture. Keep
splitting the newly created pane and you halve a half, so a request for three across yields
**1/2 · 1/4 · 1/4** (measured: widths 129 · 64 · 64).

`--ratio` is **the share the original pane keeps** (measured). To build n equal columns, give the
original `1/n`, then `1/(n-1)`, and so on. Since the remaining space shrinks with every split,
**that share grows with each round** — for three it is 0.33 then 0.5; for four, 0.25 · 0.33 · 0.5.
Start from 0.5 instead and the first column takes half, with each later one narrower.

```bash
# three equal columns — measured widths 85 · 86 · 86
A=$(herdr pane split --current --direction right --ratio 0.33 --cwd "$PWD" --no-focus \
    | python3 -c 'import sys, json; print(json.load(sys.stdin)["result"]["pane"]["pane_id"])')
herdr pane split --pane "$A" --direction right --ratio 0.5 --cwd "$PWD" --no-focus
```

Stacking works the same way with `--direction down`. **Once one axis is right, verify on the spot
that the other axis works through the same procedure.**

You can also keep using the original as the reference, but new panes then wedge in beside the
original one after another and **the order reverses.** When the person will refer to them as "the
first, the second", build them the way shown above and attach names with `pane rename`.

## Do not keep stacking in the same direction

Stack only downward and from the fourth pane on, each one is around ten rows and **unreadable.**
Splitting a 71-row pane downward three times in herdr produced 36 · 18 · 17 rows (measured). Only
stacking across does the same thing.

Before splitting an already narrow pane again, consider splitting on the other axis or sending it to
a separate tab. Creating a new tab happens only when the user asks, but **asking beats creating an
unreadable pane.**

## The direction of a resize means something else than the direction of a split

`split --direction` is **where the new pane goes**, but `resize --direction` means **push that
boundary of the target pane in that direction.** The same argument name points at different things.

So **passing the opposite direction does not undo it.** In three columns, giving `left` to the middle
pane moves its left boundary, and giving `right` to the same pane moves its right boundary. Those are
different boundaries, so chaining the two skews the layout further (measured: each changed a
different split's ratio).

- `--amount` is not a column count but **a change in ratio.** `0.1` moves that split's ratio by 0.1.
- If you intend to undo, **write down the `ratio` from `splits` before changing it** and restore that
  value.
- When all you need is one pane bigger, do not touch sizes — zoom instead. It is far easier to undo.

```bash
herdr pane zoom <pane_id> --toggle
```

## Do not touch layout mid-sequence while opening several

Adjust size or position while opening panes in sequence and the next split treads on it again. This
shows up most often when restarting several sessions one after another.

**Open them all, then tidy once.** herdr has no command that arranges a grid in one step, so getting
it right with `--ratio` at creation beats fixing it afterwards.

## When an instruction has several readings, offer the candidates before acting

Words like "evenly", "into three", "on top", "tidy this up" **produce different pictures.** There is a
case where one layout was reworked three times: four columns were applied when the person wanted
three, and the top/bottom composition differed on the next attempt.

With two or more candidates, describe what each would look like **before touching the screen** and
let them pick. When words are awkward, draw it.

```
three columns                one column + two stacked on the right
+------+------+------+       +--------+---------+
|      |      |      |       |        |         |
|  p1  |  p2  |  p3  |       |   p1   +---------+
|      |      |      |       |        |         |
+------+------+------+       +--------+---------+
```

## Report a layout you cannot express instead of routing around it

When herdr's commands will not produce the layout you want, do not force it by moving panes
repeatedly or find a path that bypasses herdr. Doing so **papers over the problem here and leaves the
same trap for the next person.**

Here is what herdr cannot express today.

- **Arranging a grid in one step.** Stacking splits one at a time is the only way.
- **Splitting directly to the left or upward.** You have to split and then swap.
- **Flipping a split's direction after the fact.** Turning a left/right pair into top/bottom means
  moving panes or rebuilding them.
- **Moving a pane within its own tab in one step.** It takes the two-step move through a temporary
  tab described above; that procedure is the supported route, not a way around this section.

A layout you cannot express is **something the tool cannot do yet**, not something a person should
put up with. State what was asked and how far you got, and that becomes a candidate for the next
extension.

## Do not steal the person's focus

Do not move focus when creating panes or running commands as background work. Move focus only when
the user asks directly, as in "take me over there".

```bash
herdr pane split --current --direction right --cwd "$PWD" --no-focus
herdr pane split --current --direction down  --cwd "$PWD" --no-focus
```

Moving focus is relatively easy to undo, but **it breaks the person's context if they were reading or
typing.** When the situation calls for an alert, raising a notification is an alternative to moving
the screen.

```bash
herdr notification show "tests finished" --body "results are in the reviewer pane" --sound done
```
