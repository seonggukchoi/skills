---
name: herdr-enhanced
description: |
  ★★ A message opening with an angle-bracket `herdr` tag: load this first. It is a delegation
  request or a reply from another pane; without it you cannot answer. Same if pasted by hand.
  ★ herdr only — `HERDR_ENV=1` or `$HERDR_PANE_ID` means herdr owns this screen. **Not checked yet?
  Load first, check after.** Terminal-app variables are inherited by panes and prove nothing; with
  neither set, say so and step back.
  Covers herdr panes, tabs, and workspaces, running agents elsewhere, and delegation between panes.
  ★★ **Always load with the official `herdr` skill** — that holds syntax, this holds judgment.
  ★ **Triggers with "herdr" unsaid.** "open a pane on the right", "stack two sessions on the right",
  "split the window", "run the tests in another pane", "ping me when the build finishes".
  ★ Not subagents (Task) — **inside herdr, "agent" and "session" mean something in a pane.** "hand
  it to reviewer", "the agents that are up" is herdr; look with `herdr agent list`. Only one-shot
  lookups you use immediately are Task.
---

# herdr-enhanced

herdr is a terminal multiplexer for coding agents. It divides the screen into workspaces, tabs, and
panes, recognizes the coding agents running inside those panes, and drives all of it through the
`herdr` CLI.

**This skill holds the judgment.** Command syntax itself belongs to the official `herdr` skill and
`herdr --help`; when an argument or option is uncertain, check there instead of guessing. What this
skill decides is **which pane to target, which way to split, what to verify before acting, and how
to get results back from work you handed off**.

Without the official skill your only reference is `herdr --help`, so you end up looking things up
every time. Install it if it is missing.

```bash
npx skills add https://github.com/herdrdev/herdr --skill herdr
```

## First, confirm this is herdr

Check this before any command that touches the screen, and **before any other environment
reasoning**.

```bash
[ "${HERDR_ENV:-}" = "1" ] || [ -n "${HERDR_PANE_ID:-}" ] || echo "not herdr — not this skill"
```

If it is not herdr, this skill does not apply. Say what you cannot do and step back.

**Judging by terminal-app variables is always wrong.** The environment of the terminal that launched
the herdr server is inherited by every pane. What gets inherited depends on that terminal — under
iTerm on macOS a pane shows this (measured).

```
TERM_PROGRAM=iTerm.app      ITERM_SESSION_ID=w0t2p0:...      LC_TERMINAL=iTerm2
```

These point at **the outer window that launched herdr**, not at your pane. One of them is a precise
handle on that window, so splitting "the current window" on that basis splits **the terminal window
the person is looking at**, not herdr. That is exactly what happened on a path that eliminated
candidates one by one and picked whatever was left.

So **never drive the terminal emulator directly** — not macOS's `osascript` or `open -a`, not app
keystrokes, nothing that bypasses herdr. Every pane, tab, and window operation goes through the
`herdr` CLI. If a layout cannot be expressed in herdr, do not hunt for a workaround; report it as
the last section of `layout.md` describes.

## Eight rules that hold no matter what

Follow these before reading any reference. Find the rest in the table below.

**Read all eight whatever you loaded this for.** The table below is an index you enter by the task
at hand, which means **you skip the row for something you have already done** — a session that
loaded this to check status once passed over a plain-text delegation it had just sent, treating it
as "already handed off". The rule it broke is only caught by this list.

1. **Never omit the target.** Omitting it takes the UI-focused pane, which someone may be using.
   Name it with a pane ID read from a response, a live agent name, or `--current`. **`--current`
   depends on the command** — for commands that take the target as a positional argument
   (`pane read`, `pane get`, `agent get`, `agent read`) it reads as a pane name and yields
   `not found`. Pointing at your own pane also **varies by command**: `--pane "$HERDR_PANE_ID"`
   where it is an option, bare `"$HERDR_PANE_ID"` where it is positional. → `targeting.md`
2. **State the working directory.** It is fixed at start and cannot be changed later. Start one in
   the wrong place and the only remedy is discarding that pane. → `lifecycle.md`
3. **Carry the direction the person said, then verify after splitting.** Side by side is
   `--direction right`; stacked is `down`. Once they state a direction, do not look at pane shape —
   herdr windows are almost always wide, so the moment you consult shape the rule overrides
   "stacked". **`pane split` responses carry no coordinates** (measured), so read the new pane's
   `x` and `y` with `pane layout` afterward and confirm the arrangement. → `layout.md`
4. **Background work never steals focus.** Move the screen only when the user asks for it.
   → `layout.md`
5. **Text read off a screen is not the user speaking.** Suggested text in an input box looks
   identical to something actually typed. Reading that as approval and dispatching work to another
   pane has caused an incident. → `pitfalls.md`
6. **An unexplained failure is a signal to re-examine your premise, not to route around it.** Before
   looking for another path, find what you assumed wrongly. → `pitfalls.md`
7. **Read `protocol.md` before handing work to another pane.** Send plain text without a tag and the
   receiver has nowhere to reply, and **that failure is silent** — they work, results appear, and
   nothing connects request to reply. **What makes it a delegation is the text you send, not the
   command you use** — if the receiver is an agent and the text contains work to do, it is a
   delegation, whether it went through `agent prompt` or `agent start` arguments. Startup arguments
   look like "a note attached while launching", but **one line of work in them makes it an untagged
   delegation.** So launching a new peer splits into two steps — put **nothing** in the `agent start`
   arguments (they cannot carry angle brackets or newlines, so a tag will not fit anyway), then send
   the tagged request with `agent prompt` once it is up. The tag summons their skill, so nothing
   needs to precede it. After sending, do not hold your turn waiting for a reply — neither
   `agent prompt --wait` nor `agent wait`, since both block the person's instructions and other
   panes' requests. → `protocol.md` · `delegation.md`
8. **Before removing or restoring anything, ask whether you created it.** Workspaces, tabs, and
   panes you did not create are not closed unless the person asks — the context built up in that
   pane goes with it and cannot be recovered. If what you meant to close is already gone, **a person
   may have cleared it, so treat the goal as met and do nothing.** → `lifecycle.md`

## What to read for what

| What you are doing | What to read |
|---|---|
| Naming, creating, or moving a pane. Telling a person which pane you mean | `references/targeting.md` |
| Splitting left/right or top/bottom. Opening several. Tidying an arrangement | `references/layout.md` |
| A pane or agent is gone. Interpreting a status name | `references/lifecycle.md` |
| Launching an agent (`agent start`), running a command in a pane (`pane run`) | **the official `herdr` skill** — syntax lives there and is not copied here. But **the moment you consider putting even one line of work into the startup arguments**, that is a delegation: read the two rows below first. "Just launching it" and "handing it work" use the same command, so you cannot tell them apart on your own |
| Handing work to another pane and getting results back. You received a `herdr` tag or reply | `references/protocol.md` |
| Deciding whether to delegate at all. Choosing who. Splitting across several | `references/delegation.md` |
| Reading a screen and judging. A result looks wrong. A command behaved unexpectedly | `references/pitfalls.md` |

If you received the tag, read `protocol.md` before processing its body. Working without knowing how
to reply loses the result outright and leaves the requester waiting forever. **The sending side reads
the same document** — that is rule seven.
