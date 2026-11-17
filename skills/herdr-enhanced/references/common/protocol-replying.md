# Replying to a request

The tag format is in [protocol-tag.md](protocol-tag.md). This file covers what the receiving side
owes and how a reply has to land. The send itself differs by CLI:
[tui/replying.md](../tui/replying.md) (the reply block: status query, `esc` interrupt, `agent_blocked`) ·
[app/replying.md](../app/replying.md) (`hc send`, the `blocked` and `finished` refusals).

## Replying is an obligation

Once you receive a request, **reply under all circumstances.** The requester holds that work open
until a reply arrives, and with no reply they wait forever.

| Outcome | `status` | When |
|---|---|---|
| Done | `ok` | You finished what was asked |
| Failed or impossible | `failed` | You could not. **Include the reason** — the requester can find another route |
| In progress | `partial` | It will take a while. Report that you started and the expected duration first, then send `ok` when done |

**Silence is the worst outcome.** Failures get a reply too.

**Reply only to the tag's `reply`.** Not to `from`, and not to whoever pushed the text into your
pane: in hc mode the `<hc from>` wrapping names the sender, which differs from `reply` after a
handover ([app/addressing.md](../app/addressing.md)).

**Copy tag values across verbatim.** `res` is the `id` you received, `to` is the `reply` you
received, and `fanout` echoes the value you received. Build the body with a heredoc, not inside
single quotes — replies commonly contain apostrophes, which close the quote right there and break the
whole command. For long results, write a file and send its path.

**Process and reply even to a malformed tag.** Discard a message because a closing tag was missing or
one attribute was absent, and the sender waits without knowing why. Work from as much as you can
read, and note what was missing in your reply so they fix it next time.

Once you receive a reply (`res`), **it ends there.** Reply to a reply and you start a ping-pong.
`reply` and `hop` are absent from reply tags because a reply is the terminus.

You may receive a `res` for something you never sent. That happens when another side handed work over
and named you as the reply address. Do not discard it as unfamiliar; use `from` to pick up the
context.

## A reply must reach a requester who is busy

Send a reply plainly while the requester is working and, depending on the agent, it may queue, so the
requester finishes that turn **knowing only the replies that arrived earlier** and reads yours
afterwards. On a request spread across several places, that delay becomes pure loss — a reply that
overturns the conclusion arrives after the work has already set, and it has to be undone or redone
from scratch.

How this is met differs by carrier (the hc behavior below is measured):

- **TUI**: a plain `agent prompt` just queues, so the reply cuts the requester's turn with `esc`
  first and marks `interrupted` ([tui/replying.md](../tui/replying.md)).
- **hc**: with Claude Code, a message sent while it was `working` was fed into the running turn at
  the next tool-call boundary, so the reply is sent with `hc send` and nothing is cut
  ([app/replying.md](../app/replying.md)).

**Do not interrupt requests (`id` tags).** New work is right to process in order, and there is no
grounds for cutting into what someone else is doing. The only thing that ever gets interrupted is a
reply the other side was holding work open for.

## Check every send

A refused send means **the reply did not go through.** Fail to check whether it succeeded and you
will report a reply as delivered when it was not — which is the silence this contract calls the worst
outcome.

- **The requester is `blocked`**: they are waiting on a person's answer. Interrupting makes that
  question disappear, and the tools refuse the send anyway. Tell the user, and send again after that
  answer is handled.
- **The requester is gone**: tell the user where the result is.

## Distinguish having sent from having been received

A successful send means **the text was delivered to the other side**, not that they started a turn.

There is an incident that blurred the two. A send to a target whose status could not be queried was
taken as receipt, the safety net was removed, and **the replies to a delegation spread across several
branches all evaporated.** The work was all done and only the results were gone, so from the sending
side it looked as though the delegation itself had never happened.

- Check the status where you can, to see whether they moved.
- **Where you cannot check, record that you cannot.** Do not promote having sent into having been
  received.
- Do not resend immediately because a check failed. That produces a duplicate submission
  ([diagnosing.md](diagnosing.md) explains why a failed confirmation is not a reason to resend).
