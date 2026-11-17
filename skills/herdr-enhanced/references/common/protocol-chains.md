# When the chain grows long

The tag format is in [protocol-tag.md](protocol-tag.md). This file covers work you took on that needs
yet another pane: asking it yourself, handing over, and how far a chain may go.

If work you took on **needs another pane, speak to that pane directly.** Bouncing "please ask them"
back to the requester turns them into a relay, doubling the round trips and wearing down context in
the retelling.

| Situation | How to send | Reply flow |
|---|---|---|
| **Supporting query** — you need the answer to synthesize | Request with `hop` raised by one | colleague → you → requester |
| **Handover** — they are the right one to finish it | Raise `hop` by one and set `reply` to the original requester | colleague → **straight to the requester** |

**Keep the original request's `id` even when handing over.** The requester can only tell which request
an answer belongs to by the `id` they sent. Mint a new `id` while handing over and **an answer they
have never seen** arrives, leaving the open request unclosable. A `res` for something you never sent
([protocol-replying.md](protocol-replying.md)) is about **a third party merely named as the reply
address**; what goes to the original requester is always the `id` they sent.

After handing over, **tell the requester with a `partial` that you did so.** Without that, the
requester stalls waiting on your reply.

`hop` is judged on **the value after adding one.** Received 3 means the raised value is 4, so it is
not passed on. A chain that long is a signal that the request's scope was drawn wrong, so reply to
the requester with that fact instead of passing it on.

In hc mode, children do not start agents unless explicitly assigned (hc's manual); keep that
alongside `hop`: re-delegating to a new agent needs the request to allow it.

**Include the collaboration record in your reply.** Write who you exchanged what with and what came of
it. The requester is not relaying, but they need to know what happened to make the next call.
Otherwise they will order the same investigation again.
