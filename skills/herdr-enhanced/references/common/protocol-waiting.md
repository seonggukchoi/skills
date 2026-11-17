# Waiting for replies

The tag format is in [protocol-tag.md](protocol-tag.md). This file covers the requester's side after
sending: not blocking, and not concluding before every reply is in.

How each CLI waits:
[tui/delegating.md](../tui/delegating.md) (end the turn; no `agent prompt --wait`, no `agent wait`) ·
[app/delegating.md](../app/delegating.md) (end the turn, or `hc wait --children`).

## End your turn after delegating

Once you have sent a request, **do not poll while waiting for the reply.** Leave one line about what
you are waiting on and end the turn. The reply arrives later as a new message, and why you asked is
still right there in the conversation.

**Blocking stops the person's instructions and other sides' requests along with it.** So any wait
that holds your turn until a reply comes back is out. In hc mode `hc wait --children` is the
exception, because it also returns when a message reaches you and so shuts nobody out; never
sleep-and-poll in either mode.

The same holds when spreading work to several places at once. They will not arrive in order, but `id`
tells you which request each answers.

## Do not synthesize before every reply is in

It is better **not to start work that a late reply would overturn.**

When spreading work, carry the branch count as `fanout` in the request tag, and the receiving side
echoes that value back in its reply. herdr keeps no central record of who is waiting on what (hc
tracks parents and children, not which request a reply answers), so
**the requester's own conversation context is the only ledger.** The branch count in the tag supports
that ledger.

When one reply arrives:

| Situation | What to do |
|---|---|
| Fewer replies received than the `fanout` value | **Do not start synthesis, judgment, or implementation.** Note what arrived in one line, write down what you are still waiting on, and end the turn |
| This is the last reply | Combine what you have and proceed |
| In the TUI, it carries `interrupted="1"`, or a tool call just above it shows as rejected or interrupted | The sender cut your turn to deliver it; do not stop. What to rerun is in [tui/replying.md](../tui/replying.md) ("When a reply cut your turn") |

Work unrelated to the replies is fine while waiting. All that is blocked is settling **a judgment that
hangs on the replies** ahead of time.
