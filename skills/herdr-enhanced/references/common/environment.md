# Which environment you are in

Every screen operation rests on one judgment made first: **is this herdr, and which kind.** Get it
wrong and every command after it lands on a screen it was never meant for. The check itself is in
[SKILL.md](../../SKILL.md) ("First, confirm this is herdr"); this document holds why it is done that
way.

## Judge on positive evidence

- **herdr TUI**: `HERDR_ENV=1` or `HERDR_PANE_ID` is set.
- **herdr app (hc mode)**: `HC_TERMINAL_ID` is set; that value is your own address.
- **Neither**: this skill does not apply. Say what you cannot do and step back.

Each of these needs no elimination. **If you cannot reach a judgment, stop before touching the
screen.** A screen split without knowing which environment you are in leaves the undo to a person.

## Terminal-app variables point at the window that launched herdr

The environment of the terminal that launched the herdr server is inherited by every pane. What gets
inherited depends on that terminal — under iTerm on macOS a pane shows this (measured).

```
TERM_PROGRAM=iTerm.app      ITERM_SESSION_ID=w0t2p0:...      LC_TERMINAL=iTerm2
```

On that terminal, `TERM_PROGRAM`, `TERM_PROGRAM_VERSION`, `ITERM_SESSION_ID`, `LC_TERMINAL`, and
`TERMINFO_DIRS` all carried the outer window's values (measured), and among them `ITERM_SESSION_ID`
**addresses exactly the window herdr was launched from**, so acting on it drives commands straight
into someone else's screen. On a different terminal the variable names change but the structure is
the same.

**Terminal-app variables tell you only "what launched herdr."** They say nothing about where you are.

`tty` does not help here either. Commands inside a pane usually report `not a tty`, so trying to
compare that against the outer window yields no conclusion.

## Do not narrow down to the environment by elimination

Crossing candidates off one at a time and then picking the most plausible survivor **produces an
answer with herdr missing from the candidate list.** This actually happened inside a herdr pane.

1. Multiplexer candidates were crossed off using environment variables.
2. A terminal-app variable was still set, so that app was concluded to be the host.
3. That app was driven to split "the current window" left/right and top/bottom. **The outer window
   the person was using got carved up.**

All three steps make sense individually and the conclusion is wrong.

## Never drive the terminal emulator directly

Not macOS's `osascript` or `open -a`, not app keystrokes, nothing that bypasses herdr. Every pane,
tab, and window operation goes through the `herdr` CLI in the TUI, and through `hc` and the app's own
tooling in hc mode. If a layout cannot be expressed that way, do not hunt for a workaround; report it
as [layout-arranging.md](layout-arranging.md) ("Report a layout you cannot express") describes.
