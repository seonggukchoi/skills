# Opening several panes, sizes, focus, and what cannot be expressed

The direction of a single split and checking it are in
[layout-direction.md](layout-direction.md). This file covers what comes after: several panes at once,
ratios, resizing, ambiguous instructions, focus, and layouts the tool cannot build.

How to carry it out:
[tui/sizing.md](../tui/sizing.md) (`--ratio` per split for equal panes, `resize` direction meaning,
zoom, notifications) ·
[tui/rearranging.md](../tui/rearranging.md) (same-tab moves, `pane swap` versus the two-step move) ·
[app/layout.md](../app/layout.md) (`open --ratio`, `resize --ratio 2:1[:1]`, `move-tab`, `adopt`).

## When creating several, fix the reference pane and the ratios up front

**Unless the person states a ratio, divide as evenly as possible** — every pane gets the same share
by default.

Even with the right direction, **which pane you split for the nth one** changes the picture. Keep
splitting the newly created pane and you halve a half, so a request for three across yields
**1/2 · 1/4 · 1/4** (measured in the TUI: widths 129 · 64 · 64). Set each split's ratio at creation
so the shares come out equal; the arithmetic for the TUI is in [tui/sizing.md](../tui/sizing.md),
and `hc-layout` sets a whole split's weights in one `resize`.

**Once one axis is right, verify on the spot that the other axis works through the same
procedure.** Building columns correctly says nothing about whether stacking works.

When the person will refer to the panes as "the first, the second", build them in that order and
name them.

## Do not keep stacking in the same direction

The official skill already warns against repeated same-direction splits. How fast it degrades:
splitting a 71-row pane downward three times produced 36 · 18 · 17 rows (measured in the TUI), and stacking
across does the same.

Before splitting an already narrow pane again, consider splitting on the other axis or sending it to
a separate tab. Creating a new tab happens only when the user asks, but **asking beats creating an
unreadable pane.**

## Changing sizes

- If you intend to undo, **write down the current ratio or weights before changing them** and
  restore that value. Resizing in the opposite direction does not reliably undo a resize (the TUI's
  reason is in [tui/sizing.md](../tui/sizing.md)).
- When all you need is one pane bigger for a while, do not touch sizes — zoom instead. It is far
  easier to undo.

## Do not touch layout mid-sequence while opening several

Adjust size or position while opening panes in sequence and the next split treads on it again. This
shows up most often when restarting several sessions one after another.

**Open them all, then tidy once.** Getting it right with ratios at creation beats fixing it
afterwards.

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

## Do not steal the person's focus

Background work never moves focus. Move it only when the user asks directly, as in "take me over
there". Moving focus is relatively easy to undo, but **it breaks the person's context if they were
reading or typing.** When the situation calls for an alert, raise a notification instead of moving
the screen. Which commands move focus as a side effect is in
[tui/rearranging.md](../tui/rearranging.md) (`pane swap` does) and [app/layout.md](../app/layout.md)
(nothing in `hc-layout` takes focus).

## Report a layout you cannot express instead of routing around it

When the commands will not produce the layout you want, do not force it by moving panes repeatedly or
find a path that bypasses the tool. Doing so **papers over the problem here and leaves the same trap
for the next person.**

A layout you cannot express is **something the tool cannot do yet**, not something a person should
put up with. State what was asked and how far you got, and that becomes a candidate for the next
extension. What each side cannot express today is listed in [tui/sizing.md](../tui/sizing.md) ("What
the herdr TUI cannot express") and [app/layout.md](../app/layout.md) ("Limits that hold on either
route").
