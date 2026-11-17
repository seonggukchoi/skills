# What is frozen at creation, and what is already gone

Two irreversible things. Both are the kind you notice **only after it is too late**, so checking up
front is the only defense.

How to carry it out:
[tui/lifecycle.md](../tui/lifecycle.md) (`--cwd`, ending only the agent with its own exit command,
listing without narrowing scope) ·
[app/lifecycle.md](../app/lifecycle.md) (`hc kill` and `hc rm` on what you started, parent and child
lifetimes, `--outlive-parent`, what `hc-layout` leaves running).

## The working directory is fixed at start time

A coding agent's working directory **is decided the moment it starts and cannot be changed
afterwards.** Project history is filed under that path too. If you realize later that you started it
in the wrong place, **there is no way out but closing that pane and making it again.**

- When the repository to work in is already settled, **pass that path from the start.** Inheriting
  the calling pane's location is the default; if the user named a different repository, pass that
  path. A split that names no directory quietly uses the current location of the shell it splits.
- The creation response carries the path. **Check that line right there.** Catching it here is
  cheap.

## Close only what you created

Workspaces, tabs, panes, and terminals you did not create are not closed unless the person asks —
the context built up in that pane goes with it and cannot be recovered. There is a case on record of
a whole session started in a home directory being thrown away; everything accumulated until then
went with it.

- If the misplaced thing is a pane you just made yourself, closing it is fine.
- **If you put an agent on a pane the person was already using, keep the pane** and end only the
  agent, with that agent's own exit command.
- **If that does not work either, ask the user rather than closing the pane.** herdr will not tell
  you whether you created something (there is no creator field; not checked for hc), so your own
  conversation history is the only evidence — if you do not remember, treat it as not yours and
  ask.

## Do not resurrect what is gone on your own

If a pane you meant to close is already gone, **you did not fail to find it — the goal is already
met.** Doing nothing is the right answer.

**The person may have cleaned it up themselves.** Recreating it without checking undoes a screen
they deliberately tidied. This has actually happened. If you need evidence, query the full list
(do not narrow its scope; it may have moved); whether to bring it back is the person's call.

## The revived side does not know it was cut off

The smoother the restore, the less the disconnect is visible to the one who lived it. A revived
session once corrected its questioner with "I was alive the whole time." In fact it had ended and
been restored.

That session knew about the trap and went looking for external evidence to decide, but **the
evidence it found happened to carry no history, which only gave a wrong conclusion more
confidence.** The lesson: **"thinking you have an instrument when you do not" is worse than having
none.**

herdr's queries show current state and carry no history. (hc keeps an ended terminal readable with
`hc read` until it is removed, but how much history that covers was not measured.) So absence from a
query result must never be read as "it never happened." What you cannot verify, **say you cannot
verify.**

## Do not read a status name as a conclusion

The statuses attached to agents are observations, not verdicts; their meanings are in the official
`herdr` skill's "Understand layout, panes, and agents" (TUI) and `hc --skill` (hc mode). Two readings
to hold on to: `done` does not mean anyone saw the result, and `blocked` is not a failure, so look at
what is being asked first.
