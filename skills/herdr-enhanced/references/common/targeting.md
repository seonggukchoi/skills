# Targets and reference points

This is where screen operations go wrong most often. The command itself succeeds, but **it lands on
the wrong pane.** The failure never surfaces as an error — it quietly rearranges someone else's
screen — so the person is usually the one who notices.

How to name a target with each CLI:
[tui/targeting.md](../tui/targeting.md) (`--current` and `$HERDR_PANE_ID` per command, checking a
name before sending, membership checks) ·
[app/addressing.md](../app/addressing.md) (`tN` addresses, the `<hc>` wrapping, a first request
without `to`).

## "Here" is the pane the instruction arrived in, not the pane the person is looking at

"open a pane on the right", "put it beside this", "run it here" — the reference point for every one
of these is **the pane that received the instruction**. That holds even when the person is working
in another tab at this moment. They spoke **to you**; they did not point at whatever was on their
own screen.

Omit the target and many commands fall back to **the UI-focused pane**. That pane may be in active
use by the person, or belong to another client entirely. An incident of exactly this shape has
happened: a session running in the background received "open it on the right", split the active
window, and the full-width window the person had been using became half-width.

So **not omitting the target is the default.** Use your own pane as the reference point, and pass
another pane's address **only when the person named a different place.** When a tool does not know
where it stands, the person's own eyes have to fill that gap.

## Name the target with an address read from the tool

| Situation | How to address it |
|---|---|
| The calling pane itself | Your own address, from the environment (TUI `$HERDR_PANE_ID`, hc `$HC_TERMINAL_ID`) |
| Another pane | An address read out of a response or a listing |
| A specific agent | In the TUI, a live, unique agent name. In hc mode, never a name (see below) |

**A name is recycled, so it bites on long delegations.** A name follows the current occupant of a
pane: it is released when they finish and another agent can take it over. Hold a reply address as a
name, send to it twenty minutes later, and the name may have changed hands in the meantime,
**dropping your result into an unrelated session.** Addresses you have to hold for a while should be
pane IDs (TUI) or `tN` addresses (hc), or verify right before you send that the name still points at
the same target. In hc mode this is absolute: names are never addresses
([app/addressing.md](../app/addressing.md)).

## When resolution fails, stop — do not silently fall back

Ignoring the location a person specified and opening somewhere arbitrary **betrays the intent of
that specification.** This fallback has caused an incident where the person moved the pane by hand
afterwards: the skill handed its own job back to them.

- If you cannot pin down the target, **do nothing and say so.** Do not fill the gap with a guess.
- Do not fall back to an empty value or a default. **An empty target is not "no target" — it is read
  as "the current screen."**
- If several candidates fit, do not narrow it yourself; ask which one.

## Use names when speaking to people

An ID like `w1:p3` or `t9` is **the most precise address a command argument can take**, so use it
there. But translate it to a name when you carry it back to a person. People remember by name, not
by position or number.

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

So check membership after opening several panes. If a pane you just opened is not in your tab, it
has drifted; pull it back next to the pane it belongs beside. Leave the layout wrong and the person
moves it by hand — at which point there was no reason to use this tool at all. The commands are in
[tui/targeting.md](../tui/targeting.md) ("Check membership") and, in hc mode,
[app/layout.md](../app/layout.md) (`where`, `tree`, `place`).
