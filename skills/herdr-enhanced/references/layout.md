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
The place the person was looking at changes, so say in your report that you swapped.

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

If it came out wrong, **fix it before handing back to a person.** Move the pane you already made
with `pane move --split`, or close it and split again if it is empty.

## When creating several, fix the reference pane and the ratios up front

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
