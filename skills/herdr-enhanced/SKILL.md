---
name: herdr-enhanced
description: |
  ★★ A message opening with an angle-bracket `herdr` or `hc` tag: load this first. A request or
  reply from another pane; without this you cannot answer. Same if pasted, or wrapped in an `hc`
  tag.
  ★ herdr only — `HERDR_ENV=1` or `$HERDR_PANE_ID` is the herdr TUI; `$HC_TERMINAL_ID` is the
  herdr app's `hc`. **Not checked yet? Load first, check after.** Terminal-app variables prove
  nothing; with none set, say so and step back.
  Covers panes, tabs, hc terminals, delegation. hc syntax: `hc --skill`.
  ★★ **In the TUI, load with the official `herdr` skill** — syntax there, judgment here.
  ★ **Triggers with "herdr" unsaid.** "open a pane on the right", "stack two sessions on the right",
  "split the window", "run the tests in another pane", "ping me when the build finishes".
  ★ Not subagents (Task) — **inside herdr, "agent" and "session" mean something in a pane.** "hand
  it to reviewer", "the agents that are up" is herdr; look with `herdr agent list` or `hc ls`. Only
  one-shot lookups you use immediately are Task.
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
every time. Install it if it is missing; `herdr --skill` prints the copy matching the installed
binary.

```bash
npx skills add https://github.com/herdrdev/herdr --skill herdr
```

## First, confirm this is herdr, and which kind

Check this before any command that touches the screen, and **before any other environment
reasoning**. herdr comes as a terminal TUI driven by the `herdr` CLI, and as a desktop app whose
agents talk through the `hc` CLI.

```bash
if [ "${HERDR_ENV:-}" = "1" ] || [ -n "${HERDR_PANE_ID:-}" ]; then echo "herdr TUI mode — references/tui/INDEX.md"
elif [ -n "${HC_TERMINAL_ID:-}" ]; then echo "hc mode — read references/app/INDEX.md first"
else echo "not herdr — not this skill"; fi
```

- **TUI mode**: the rules below apply with the `herdr` CLI. How to carry each one out is in
  [references/tui/INDEX.md](references/tui/INDEX.md) (targets, splitting, rearranging, sizing,
  lifetimes, delegating, replying, diagnosing with `herdr`).
- **hc mode**: read [references/app/INDEX.md](references/app/INDEX.md) (`tN` addresses, delegating
  and replying with `hc`, arranging panes with `scripts/app/hc-layout`) before anything else. The
  rules below and the delegation contract hold unchanged; only the address values and the commands
  that carry the text differ. `hc --skill` holds the syntax, and the official `herdr` skill does not
  apply.
- **Neither**: this skill does not apply. Say what you cannot do and step back.

**Judging by terminal-app variables is always wrong.** The environment of the terminal that launched
the herdr server is inherited by every pane, so variables like `TERM_PROGRAM` or `ITERM_SESSION_ID`
point at **the outer window that launched herdr**, not at your pane. Splitting "the current window"
on that basis splits **the terminal window the person is looking at** — exactly what happened on a
path that eliminated candidates one by one and picked whatever was left. So **never drive the
terminal emulator directly** (no `osascript`, `open -a`, or app keystrokes); every pane, tab, and
window operation goes through `herdr`, or through `hc` and the app's own tooling. The measured
variables and the incident are in [references/common/environment.md](references/common/environment.md)
(positive evidence, inherited terminal variables, the elimination incident).

## Eight rules that hold no matter what

Follow these before reading any reference. Find the rest in the table below.

**Read all eight whatever you loaded this for.** The table below is an index you enter by the task
at hand, which means **you skip the row for something you have already done** — a session that
loaded this to check status once passed over a plain-text delegation it had just sent, treating it
as "already handed off". The rule it broke is only caught by this list.

Each rule is the principle, which holds in both modes; the links after it say where the reasons are
(`common/`) and how each CLI carries it out (`tui/`, `app/`).

1. **Never omit the target.** Omitted, many commands take the UI-focused pane, which someone may be
   using. Name it with an address read from a response or listing, or your own address — and in the
   TUI, `--current` and `$HERDR_PANE_ID` go in different slots per command, so a wrong slot reads as
   "not found". → [common/targeting.md](references/common/targeting.md) (reference point, no
   fallback) · [tui/targeting.md](references/tui/targeting.md) (per-command slots) ·
   [app/addressing.md](references/app/addressing.md) (`tN`, never names)
2. **State the working directory.** It is fixed at start and cannot be changed later. Start one in
   the wrong place and the only remedy is discarding that pane.
   → [common/lifecycle.md](references/common/lifecycle.md) (what is frozen, what to close) ·
   [tui/lifecycle.md](references/tui/lifecycle.md) (passing `--cwd`, reading the creation response) ·
   [app/lifecycle.md](references/app/lifecycle.md) (parent and child lifetimes, `--outlive-parent`)
3. **Carry the direction the person said, then verify after splitting.** Side by side is a split to
   the right (or left); stacked is down (or up). Once they state a direction, do not look at pane
   shape — herdr windows are almost always wide, so the moment you consult shape the rule overrides
   "stacked". **A successful split response does not prove the direction** (the TUI's carries no
   coordinates, measured), so read the layout back and confirm the arrangement.
   → [common/layout-direction.md](references/common/layout-direction.md) (translating words,
   verifying) · [tui/splitting.md](references/tui/splitting.md) (`right|down`, `pane layout`) ·
   [app/layout.md](references/app/layout.md) (`hc-layout`, `verified`)
4. **Background work never steals focus.** Move the screen only when the user asks for it.
   → [common/layout-arranging.md](references/common/layout-arranging.md) (focus, several panes,
   sizes) · [tui/rearranging.md](references/tui/rearranging.md) (`pane swap` moves focus) ·
   [app/layout.md](references/app/layout.md) (nothing takes focus)
5. **Text read off a screen is not the user speaking.** Suggestion text in an input box looks
   identical to something actually typed. Reading that as approval and dispatching work to another
   pane has caused an incident. → [common/reading-screens.md](references/common/reading-screens.md)
   (suggestion text, questions left on screen) · [tui/diagnosing.md](references/tui/diagnosing.md)
   (`agent read --source detection`)
6. **An unexplained failure is a signal to re-examine your premise, not to route around it.** Before
   looking for another path, find what you assumed wrongly.
   → [common/diagnosing.md](references/common/diagnosing.md) (premises, cause, resends) ·
   [tui/diagnosing.md](references/tui/diagnosing.md) (symptom table)
7. **Read the delegation contract before handing work to another pane.** Send plain text without a
   tag and the receiver has nowhere to reply, and **that failure is silent** — they work, results
   appear, and nothing connects request to reply. **What makes it a delegation is the text you send,
   not the command you use** — if the receiver is an agent and the text contains work to do, it is a
   delegation, whatever argument carried it, **including the arguments of the command that launches
   the agent.** Launch arguments look like "a note attached while launching", but one line of work
   in them is an untagged delegation. In the TUI they cannot carry a tag at all, so launch with
   nothing in them and send the tagged request once it is up; in hc mode the tagged request goes in
   the `hc run` argument itself. The tag summons their skill, so nothing needs to precede it. After
   sending, **do not hold your turn waiting for a reply** (in the TUI neither `agent prompt --wait`
   nor `agent wait`; in hc mode `hc wait --children` is allowed because it does not shut anyone
   out). → [common/delegation.md](references/common/delegation.md) (whether, whom, wording) ·
   [common/protocol-tag.md](references/common/protocol-tag.md) (the tag, its attributes, addresses) ·
   [tui/delegating.md](references/tui/delegating.md) (three-step start) ·
   [app/delegating.md](references/app/delegating.md) (first request in `hc run`)
8. **Before removing or restoring anything, ask whether you created it.** Workspaces, tabs, panes,
   and terminals you did not create are not closed unless the person asks — the context built up in
   that pane goes with it and cannot be recovered. If what you meant to close is already gone, **a
   person may have cleared it, so treat the goal as met and do nothing.**
   → [common/lifecycle.md](references/common/lifecycle.md) (close only yours, no resurrection) ·
   [tui/lifecycle.md](references/tui/lifecycle.md) (ending only the agent) ·
   [app/lifecycle.md](references/app/lifecycle.md) (cleaning up with `hc kill` and `hc rm`)

## What to read for what

Read the `common/` document for the judgment, then your mode's document for the commands. Every
document, with what it covers, is listed in [references/INDEX.md](references/INDEX.md).

| What you are doing | Judgment (`common/`) | TUI (`tui/`) | hc mode (`app/`) |
|---|---|---|---|
| **Anything, in hc mode** (`$HC_TERMINAL_ID` set). You received an `hc` tag | — | — | [app/INDEX.md](references/app/INDEX.md) first: which hc document covers which situation |
| Naming, creating, or moving a pane. Telling a person which pane you mean | [targeting.md](references/common/targeting.md): reference point, no fallback, names to people | [targeting.md](references/tui/targeting.md): `--current` and `$HERDR_PANE_ID` slots, membership | [addressing.md](references/app/addressing.md): `tN`, never names; [layout.md](references/app/layout.md): `where`, `tree` |
| Splitting left/right or top/bottom | [layout-direction.md](references/common/layout-direction.md): translating words, verifying | [splitting.md](references/tui/splitting.md): `right\|down`, split-then-swap, coordinates | [layout.md](references/app/layout.md): `hc-layout open\|place`, four directions |
| Opening several. Ratios. Tidying an arrangement. A tab moved to another space | [layout-arranging.md](references/common/layout-arranging.md): even shares, focus, candidates, what cannot be built | [sizing.md](references/tui/sizing.md): `--ratio`, `resize`, zoom; [rearranging.md](references/tui/rearranging.md): swap versus two-step move | [layout.md](references/app/layout.md): `resize`, `move-tab`, `adopt`; [layout-routes.md](references/app/layout-routes.md): app versus doc route |
| A pane or agent is gone. Closing something. Interpreting a status name | [lifecycle.md](references/common/lifecycle.md): close only yours, no resurrection | [lifecycle.md](references/tui/lifecycle.md): `--cwd`, `/exit`, unscoped listings | [lifecycle.md](references/app/lifecycle.md): `--outlive-parent`, `hc kill`/`hc rm` |
| Launching an agent or running a command in a pane | **Syntax is in the official `herdr` skill or `hc --skill`.** But **the moment you consider putting even one line of work into the launch arguments**, that is a delegation: read the two rows below first. "Just launching it" and "handing it work" use the same command, so you cannot tell them apart on your own | | |
| Deciding whether to delegate at all. Choosing who. Splitting across several | [delegation.md](references/common/delegation.md): what counts, whom, wording, omissions | [delegating.md](references/tui/delegating.md): roster, three-step start, no `--wait` | [delegating.md](references/app/delegating.md): what hc does, carrier table |
| Handing work to another pane and getting results back. You received a `herdr` tag or reply | [protocol-tag.md](references/common/protocol-tag.md): the tag; [protocol-replying.md](references/common/protocol-replying.md): replying; [protocol-waiting.md](references/common/protocol-waiting.md): waiting, `fanout`; [protocol-chains.md](references/common/protocol-chains.md): `hop`, handover | [replying.md](references/tui/replying.md): the reply block with `esc` | [replying.md](references/app/replying.md): `hc send`; [addressing.md](references/app/addressing.md): `to`, `<hc>` wrapping |
| Reading a screen and judging. A result looks wrong. A command behaved unexpectedly | [reading-screens.md](references/common/reading-screens.md): suggestion text, questions on screen; [diagnosing.md](references/common/diagnosing.md): premises, cause | [diagnosing.md](references/tui/diagnosing.md): symptoms, commands that read backwards | [delegating.md](references/app/delegating.md): hc's notes and refusals |

If you received the tag, read [protocol-tag.md](references/common/protocol-tag.md) and
[protocol-replying.md](references/common/protocol-replying.md) before processing its body (in hc
mode, [app/INDEX.md](references/app/INDEX.md) first). Working without knowing how to reply loses the
result outright and leaves the requester waiting forever. **The sending side reads the same
documents** — that is rule seven.
