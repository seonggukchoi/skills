# Starting places and ending things with the herdr CLI

The principles — the working directory is fixed at start, close only what you created, do not
resurrect what is gone, the revived side does not know, status names are observations — are in
[common/lifecycle.md](../common/lifecycle.md). This file is how herdr behaves around them.

## Pass the working directory

Splitting a pane **quietly uses that shell's current location** when you do not name a working
directory, which is why the official skill always passes `--cwd`. Pass the settled repository's path,
and read the `cwd` line in the creation response right away.

## Ending only the agent, not the pane

**herdr has no command that takes down only the agent** — there is no stop, kill, or close under
`agent` (measured). What is left is making that agent end itself, and that means **sending that
tool's own exit command through `agent prompt`**.

```bash
herdr agent prompt <target> '/exit'      # Claude Code's exit command. Other tools use their own
```

When it ends, the pane **remains as a shell with no agent** (measured). That is the state the "keep
the person's pane" rule was protecting.

**Sending an interrupt key does not end it.** `agent send-keys <target> ctrl+c` left Claude Code
alive even sent twice (measured). An interrupt stops work in progress; it does not end the session.

If the exit command does not work either, ask the user rather than reaching for `pane close`. herdr
has no creator field, so it cannot tell you whether you made that pane.

## Looking for something that is gone

```bash
herdr agent list
herdr pane list          # when looking for something gone, do not narrow the scope — it may have moved workspaces
```

herdr's queries show current state and carry no history; absence there is not evidence that it never
existed.
