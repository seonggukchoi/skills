# What is frozen at creation, and what is already gone

Two irreversible things. Both are the kind you notice **only after it is too late**, so checking up
front is the only defense.

## The working directory is fixed at start time

A coding agent's working directory **is decided the moment it starts and cannot be changed
afterwards.** Project history is filed under that path too. If you realize later that you started it
in the wrong place, **there is no way out but closing that pane and making it again.**

**But confirm you created that pane before you close it.** This is where the official skill's
prohibition applies: do not close a workspace, tab, pane, or session you did not create unless the
person explicitly asks. If the misplaced thing is a pane you just made yourself, closing it is fine.

**If you put an agent on a pane the person was already using, keep the pane.** The catch is that
**herdr has no command that takes down only the agent** — there is no stop, kill, or close under
`agent` (measured). What is left is making that agent end itself, and that means **sending that
tool's own exit command through `agent prompt`**.

```bash
herdr agent prompt <target> '/exit'      # Claude Code's exit command. Other tools use their own
```

When it ends, the pane **remains as a shell with no agent** (measured). That is the state this rule
was protecting.

**Sending an interrupt key does not end it.** `agent send-keys <target> ctrl+c` left Claude Code
alive even sent twice (measured). An interrupt stops work in progress; it does not end the session.

**If the exit command does not work either, ask the user rather than reaching for `pane close`.**
Closing that pane takes the context the person built up with it, irreversibly. herdr will not even
tell you whether you created it (there is no creator field), so your own conversation history is the
only evidence — if you do not remember, treat it as not yours and ask. There is a case on record of
a whole session started in a home directory being thrown away; everything accumulated until then
went with it.

Splitting a pane **quietly uses that shell's current location** when you do not name a working
directory. It is easy to end up starting in a home or skill directory.

```bash
herdr pane split --current --direction right --cwd "$PWD" --no-focus
```

- When the repository to work in is already settled, **pass that path from the start.** Inheriting
  the calling pane's location is the default; if the user named a different repository, pass that
  path.
- The creation response carries the path. **Check that line right there.** Catching it here is
  cheap.
- Do not create a new workspace, tab, or worktree unless the user explicitly asks. That goes double
  for a worktree, which means creating a new working directory.

## Do not resurrect what is gone on your own

If a pane you meant to close is already gone, **you did not fail to find it — the goal is already
met.** Doing nothing is the right answer.

**The person may have cleaned it up themselves.** Recreating it without checking undoes a screen
they deliberately tidied. This has actually happened. If you need evidence, query the list; whether
to bring it back is the person's call.

```bash
herdr agent list
herdr pane list          # when looking for something gone, do not narrow the scope — it may have moved workspaces
```

## The revived side does not know it was cut off

The smoother the restore, the less the disconnect is visible to the one who lived it. A revived
session once corrected its questioner with "I was alive the whole time." In fact it had ended and
been restored.

That session knew about the trap and went looking for external evidence to decide, but **the
evidence it found happened to carry no history, which only gave a wrong conclusion more
confidence.** The lesson: **"thinking you have an instrument when you do not" is worse than having
none.**

herdr's queries show current state and carry no history. So absence from a query result must never
be read as "it never happened." What you cannot verify, **say you cannot verify.**

## Do not read a status name as a conclusion

The statuses herdr attaches are observations, not verdicts.

| Status | What it actually means | What not to do |
|---|---|---|
| `idle` | Ready for input, and seen on a screen whose tab was focused | |
| `done` | The same idle state, after unacknowledged background work finished | Do not assume anyone saw the result |
| `blocked` | herdr recognized an approval or question screen | Do not read it as failure. Look at what is being asked first |
| `working` | Working | |
| `unknown` | An agent is there, but herdr could not classify it | **This is not evidence of completion** |

Moving focus, or calling a focus command against that pane, counts as acknowledgement. **Reading via
the CLI alone does not.** Background work staying at `done` while you only query it is normal.
