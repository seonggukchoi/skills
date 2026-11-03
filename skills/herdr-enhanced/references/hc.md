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
| **A new peer's first work arrives as a tagged request**, never as an untagged line of work | Start with nothing in the `agent start` arguments, then send the tag with `agent prompt` | **Put the tagged request in the `hc run` argument** | hc's manual says a send to a booting agent can be dropped. The argument reaches the agent intact, angle brackets and newlines included (measured), so the tag fits. Only a template launch reports whether the first message was sent; without a template the response carries no such field, so read the screen if you are unsure, and do not resend blindly |
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

## What hc does not cover

hc runs terminals; it does not arrange windows. Requests about splitting or placing panes on screen
belong to the app's own tooling (hc's manual points to it). The judgment in `layout.md` (translate
the direction the person said, verify after acting, never steal focus) applies to whatever tool does
the arranging.
