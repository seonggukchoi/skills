# Delegating with hc

Whether to delegate, choosing and wording, and the rule that the text you send makes it a delegation
are in [common/delegation.md](../common/delegation.md). The tag is in
[common/protocol-tag.md](../common/protocol-tag.md) and the `tN` addresses in
[addressing.md](addressing.md); waiting is in
[common/protocol-waiting.md](../common/protocol-waiting.md). This file is how hc carries them. `hc
--skill` holds the syntax, and `hc <command> --help` gives exact arguments.

## What hc already does: use it, do not rebuild it

| hc gives you | So in hc mode |
|---|---|
| **Parent and child.** Terminals you `hc run` are your children | They end when you end, unless started with `--outlive-parent` (below) |
| **Notes about children.** hc types a note into the parent when a child blocks, hits an error, or exits, e.g. `<hc>t9 cg exited (exit 3). Read: hc read t9</hc>` | Read that child's screen and decide about its work. Do not ask children to report "I am stuck on a dialog"; hc reports what they cannot |
| **Blocked protection.** `hc send` to a `blocked` terminal is refused unless forced | Never force it. A blocked agent is waiting on a person, as in the TUI |
| **`hc wait --children`.** Returns on a child's news, or when a message reaches you | Use it instead of sleeping or polling (below) |

Use `hc ls` and `hc get` to build the roster and read status, and drop `$HC_TERMINAL_ID` from the
roster, since `hc ls` lists every live terminal including you.

hc's manual says children do not start agents unless explicitly assigned. Keep that alongside `hop`:
re-delegating to a new agent needs the request to allow it.

## Same contract, different carrier

Each row keeps what the TUI rule protects; only the means of carrying it changes. The TUI side is in
[tui/delegating.md](../tui/delegating.md) and [tui/replying.md](../tui/replying.md).

| What the contract requires | TUI carrier | hc carrier | Why hc differs |
|---|---|---|---|
| **A new peer's first work arrives as a tagged request**, never as an untagged line of work | Start with nothing in the `agent start` arguments, then send the tag with `agent prompt` | **Put the tagged request in the `hc run` argument**, without `to` ([addressing.md](addressing.md)) | hc's manual says a send to a booting agent can be dropped. The argument reaches the agent intact, angle brackets and newlines included (measured), so the tag fits. Only a template launch reports whether the first message was sent; without a template the response carries no such field, so read the screen if you are unsure, and do not resend blindly |
| **Waiting for replies must not shut out a person or other requests** | End the turn; no `agent prompt --wait`, no `agent wait` | **End the turn, or `hc wait --children`** when the next step needs the replies | `hc wait` returns when a message reaches you, so nobody is shut out. A timeout is a check-in, not a failure. Never sleep-and-poll |
| **A reply must reach a requester who is busy** | Cut the requester's turn with `esc`, then `agent prompt`, marking `interrupted` | **`hc send` the reply**; no `esc`, no `hc interrupt`, no `interrupted` attribute ([replying.md](replying.md)) | Measured with Claude Code: a message sent while it was `working` was queued and fed into the running turn at the next tool-call boundary. Other agents were not measured |
| **A peer meant to stay outlives the work that started it** | Panes stay until closed | **Start it with `--outlive-parent`** ([lifecycle.md](lifecycle.md)) | Without it a child ends when its parent's program ends (measured) |

## A dialog on someone else's screen

**A dialog on someone else's screen is a question to a person**
([common/reading-screens.md](../common/reading-screens.md)). hc's manual mentions answering a trust
dialog with keys; do that only when the person told you to. Otherwise report what the screen shows.
