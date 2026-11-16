# hc mode

herdr also ships as a desktop app built on **herdr-core**. There, agents talk to each other through
the `hc` CLI, not `herdr`. You are in hc mode when `$HC_TERMINAL_ID` is set; that value is your own
address.

**hc has its own manual.** `hc --skill` prints it, and `hc <command> --help` gives exact arguments.
This document does not copy that syntax. It covers only **how this skill's judgment and delegation
contract run over hc**.

**The contract does not change in hc mode.** The tag, its attributes, the reply obligation, and the
synthesis rules are exactly those of `protocol.md`. Only two things differ: **the address values**,
and **the commands that carry the text**.

Measured behavior below was observed with hc 0.1.17 and Claude Code agents. Anything not measured is
marked as such.

## Addresses

Write hc addresses (`tN`) wherever `protocol.md` puts a pane ID: `to`, `from`, `reply`. Your own is
`$HC_TERMINAL_ID`; another terminal's comes from the `hc run` response or `hc ls`.

**Never use a name as an address.** A name belongs to whichever live terminal holds it. Once its
owner ends, a send by that name is refused, and as soon as another terminal takes the name, the send
lands there (measured). Addresses were not reused within a session (measured).

```
<herdr id="r7f3a2" to="t9" from="t4" reply="t4" hop="1" fanout="3">
Review the changes in the current working tree and tell me only what actually needs fixing.
</herdr>
```

```
<herdr res="r7f3a2" from="t9" to="t4" status="ok" fanout="3">
Two places. A missing expiry check in the auth middleware, and the exit condition of the retry loop.
</herdr>
```

**Reply only to the tag's `reply`**, as in the TUI. Handover, re-delegation, and `hop` work exactly as
`protocol.md` describes.

### A first request in the `hc run` argument leaves out `to`

A new peer's first request rides in the `hc run` argument (below), and its `tN` does not exist until
`hc run` returns. So **that one tag leaves `to` out.** Never fill it with a guessed `tN` or a name:
a wrong `to` is worse than none, because the receiver passes it on when re-delegating. Every other
tag, including later requests to the same peer with `hc send`, carries `to` as usual.

```
<herdr id="r7f3a2" from="t4" reply="t4" hop="1" fanout="3">
Review the changes in the current working tree and tell me only what actually needs fixing.
</herdr>
```

**When a tag you receive has no `to`, read it as your own `$HC_TERMINAL_ID`.** `to` always means
the reader's own address, so the reader can always supply it. Use that value wherever `protocol.md`
uses `to`. It changes nothing about replying: the reply still goes to `reply` and to nothing else.

## The `<hc>` tag is wrapping, not an address

When an agent sends text with `hc send`, hc wraps it: the receiver sees
`<hc from="t4 lead"><herdr id=…>` on the first line and `</herdr></hc>` at the end (measured). Text
from a terminal that reports no agent status, such as a plain shell, and a first task given as the
`hc run` argument arrive without that wrapping (measured). A first task given through an `hc run`
template arrives wrapped, with a `reach` attribute and the template's own instructions ahead of the
task (measured).

Treat that wrapping as **a delivery detail.** It says who pushed the text in, not who is waiting for
the answer. **If the `<hc from>` address and the `herdr` tag's `reply` differ, follow the `herdr`
tag.** A handover is exactly that case.

## What hc already does: use it, do not rebuild it

| hc gives you | So in hc mode |
|---|---|
| **Parent and child.** Terminals you `hc run` are your children | They end when you end, unless started with `--outlive-parent` (below) |
| **Notes about children.** hc types a note into the parent when a child blocks, hits an error, or exits, e.g. `<hc>t9 cg exited (exit 3). Read: hc read t9</hc>` | Read that child's screen and decide about its work. Do not ask children to report "I am stuck on a dialog"; hc reports what they cannot |
| **Blocked protection.** `hc send` to a `blocked` terminal is refused unless forced | Never force it. A blocked agent is waiting on a person, as in the TUI |
| **`hc wait --children`.** Returns on a child's news, or when a message reaches you | Use it instead of sleeping or polling (below) |

Use `hc ls` and `hc get` where `delegation.md` says `agent list` and `agent get`, and drop
`$HC_TERMINAL_ID` from the roster, since `hc ls` lists every live terminal including you.

hc's manual says children do not start agents unless explicitly assigned. Keep that alongside `hop`:
re-delegating to a new agent needs the request to allow it.

## Same contract, different carrier

Each row keeps what the TUI rule protects; only the means of carrying it changes.

| What the contract requires | TUI carrier | hc carrier | Why hc differs |
|---|---|---|---|
| **A new peer's first work arrives as a tagged request**, never as an untagged line of work | Start with nothing in the `agent start` arguments, then send the tag with `agent prompt` | **Put the tagged request in the `hc run` argument**, without `to` (see Addresses) | hc's manual says a send to a booting agent can be dropped. The argument reaches the agent intact, angle brackets and newlines included (measured), so the tag fits. Only a template launch reports whether the first message was sent; without a template the response carries no such field, so read the screen if you are unsure, and do not resend blindly |
| **Waiting for replies must not shut out a person or other requests** | End the turn; no `agent prompt --wait`, no `agent wait` | **End the turn, or `hc wait --children`** when the next step needs the replies | `hc wait` returns when a message reaches you, so nobody is shut out. A timeout is a check-in, not a failure. Never sleep-and-poll |
| **A reply must reach a requester who is busy** | Cut the requester's turn with `esc`, then `agent prompt`, marking `interrupted` | **`hc send` the reply**; no `esc`, no `hc interrupt`, no `interrupted` attribute | Measured with Claude Code: a message sent while it was `working` was queued and fed into the running turn at the next tool-call boundary. Other agents were not measured |
| **A peer meant to stay outlives the work that started it** | Panes stay until closed | **Start it with `--outlive-parent`** | Without it a child ends when its parent's program ends (measured). With it, the child still sends notes to the parent while the parent lives, and keeps the ended parent's address afterwards; sends to that address are refused as `finished` (measured) |

Check every reply send. A refusal means **the reply did not go through**: `blocked` means the
requester is waiting on a person, so tell the user and send after that; `finished` means the
requester is gone, so tell the user where the result is. Build the body with a heredoc, as in
`protocol.md`, and for long results write a file and send its path.

Two TUI rules hold as written:

- **A dialog on someone else's screen is a question to a person** (rule 5). hc's manual mentions
  answering a trust dialog with keys; do that only when the person told you to. Otherwise report
  what the screen shows.
- **Clean up only what you started** (rule 8): `hc kill` then `hc rm`, on terminals you launched.

## Splitting and placing: the app, or tab labels

hc runs terminals; it does not arrange windows. **Where the app's window is reachable, splitting and
placing panes belong to the app's own tooling** (hc's manual points to it; `herdr-app do pane.split`
is the split). That is also the only way to choose a direction. The judgment in `layout.md`
(translate the direction the person said, verify after acting, never steal focus) applies to
whatever tool does the arranging.

### No app window on this machine: join the tab with labels

A session on a remote machine often cannot reach the app at all: the app's own tooling fails with no
Herdr window to connect to, and that machine's `hc machine ls` does not list the machine running the
app. That is no reason to answer a "split inside this tab" request with a subagent, or to report
that splitting is impossible.

The app's documentation (`herdr-app --skill`, "The model: spaces, tabs, terminals") says the app
tags the terminals it starts with `herdr.space=<id>` and `herdr.tab=<id>`, and that **a terminal
carrying those labels appears in that tab, even if you started it yourself.** The IDs are those of
the machine the terminal runs on: drop the `<machine>/` prefix the app shows for remote IDs. An ID
the app does not know becomes a new space or tab, and a terminal without the labels does not appear
in the app at all.

So, on a machine without the app's window:

1. Read your own labels: `hc get "$HC_TERMINAL_ID" --json` and its `labels` object.
2. Start the new terminal with both values copied, and `--keep`:

   ```bash
   hc run --bg --keep --label herdr.space=<space id> --label herdr.tab=<tab id> <program>
   ```

   `--bg` returns at once instead of waiting for the program to end. For an agent, the tagged
   request goes in the argument as usual (Same contract, different carrier).

What each label set produced, compared on a remote machine with `hc get` (measured):

| Child started with | Where it appeared |
|---|---|
| The parent's `herdr.space` and `herdr.tab`, plus `--keep` | A split pane in the parent's tab |
| `herdr.space` only | A new tab in the same space |
| No labels | No tab at all; it exists only as a child terminal |

The parent in the successful case was started by the app, so it carried both labels from the start.
**A terminal started by the app can still lack `herdr.tab`** (measured on a local machine). Then the
labels alone do not tell you the tab. Where the app is reachable, find the tab holding your terminal
in `herdr-app ls`. Where it is not, tell the person the terminal will open as a new tab, and ask
before starting it.

Limits of this route:

- **No direction.** The app's documentation gives no way to choose right or below. If the person
  named a direction, say it cannot be guaranteed this way. Observed, not documented: a labeled
  terminal attaches at the end of the tab's outermost split, and a tab with one pane splits in half
  to the right.
- **It is still your child.** The labels place it on screen; hc's parent and child relationship
  stays. A terminal meant to stay after you end needs `--outlive-parent` as well (Same contract,
  different carrier).
- **Verify after starting** (rule 3): read the new terminal back with `hc get` and confirm both
  labels and `keep`. When you cannot see the screen, tell the person where it should appear and
  let them confirm.
