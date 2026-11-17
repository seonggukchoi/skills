# The request and reply tag

herdr gives you **a way to speak** to an agent in another pane, but no scheme for tying that
conversation into requests and replies; `agent prompt --wait` blocks synchronously, so there is no
path for handing off long work while carrying on with your own. This contract fills that gap. Do not rebuild what the tools already solved — text
injection, submission, and recognizing the other side's state belong to them. **All that is defined
here is the contract for the text exchanged.**

**The contract is the same in both modes.** The tag, every attribute, and every rule in the
`protocol-*` documents hold in the TUI and in hc mode alike; only the address values and the
commands that carry the text differ.

The rest of the contract: [protocol-replying.md](protocol-replying.md) (the reply obligation, status
codes, checking the send) · [protocol-waiting.md](protocol-waiting.md) (ending your turn, holding
synthesis until every reply is in) · [protocol-chains.md](protocol-chains.md) (`hop`, handover,
keeping the original `id`).

How each CLI carries it:
[tui/delegating.md](../tui/delegating.md) and [tui/replying.md](../tui/replying.md) (pane IDs,
`agent prompt`, cutting a busy requester's turn with `esc`) ·
[app/addressing.md](../app/addressing.md), [app/delegating.md](../app/delegating.md) and
[app/replying.md](../app/replying.md) (`tN` addresses, `hc run`, `hc send`).

## The tag

**The opening tag is the first line, the body follows, and the closing tag is the last line.** All
attributes go on the single opening-tag line; never wrap it.

```
<herdr id="r7f3a2" to="w1:p4" from="w1:p1" reply="w1:p1" hop="1">
Review the changes in the current working tree and tell me only what actually needs fixing.
</herdr>
```

When splitting the same item across several places, carry the branch count too. The receiving side
echoes it back in its reply, so the requester learns **how many more are coming** from the reply
itself.

```
<herdr id="r7f3a2" to="w1:p4" from="w1:p1" reply="w1:p1" hop="1" fanout="3">
Review the changes in the current working tree and tell me only what actually needs fixing.
</herdr>
```

```
<herdr res="r7f3a2" from="w1:p4" to="w1:p1" status="ok" fanout="3">
Two places. A missing expiry check in the auth middleware, and the exit condition of the retry loop.
</herdr>
```

In hc mode the same tags carry `tN` addresses (`to="t9" from="t4"`); see
[app/addressing.md](../app/addressing.md).

The closing tag is **the device that marks where the body ends.** Several replies arriving back to
back and read in one turn, or a person copying text off the screen with surrounding text mixed in,
still leave the boundary intact.

If you must show the shape of this tag inside a body, **drop the angle brackets and write the name
alone, or describe it in words.** Written verbatim, that line reads as the end of the body.

| Attribute | Meaning |
|---|---|
| `id` | The thread tying request to reply. Copy the same value into `res` when replying |
| `to` | The recipient. **That is, your own address as the reader of this tag.** Use this value when re-delegating or naming a reply address for a third party. In hc mode a first request sent as the `hc run` argument has none; read it as your own address ([app/addressing.md](../app/addressing.md)) |
| `from` | The sender |
| `reply` | **Where to send the reply.** Usually the same as `from`, but a third party when the work was handed over. Reply to this value, not to `from` |
| `hop` | Depth in the delegation chain. Add one to the value received when passing a request on. **Above 3, do not pass it on** ([protocol-chains.md](protocol-chains.md)) |
| `status` | Replies only. One of `ok`, `failed`, `partial` |
| `fanout` | **How many branches the same item was spread across.** Carried when a requester divides work among several, and the receiving side **echoes the value back in its reply** — the requester has to know how many more are pending in order to hold off synthesis |
| `interrupted` | Replies only, TUI only. A marker that **the other side's in-progress turn was cut** to insert this reply ([tui/replying.md](../tui/replying.md)) |

## Addresses

Addresses are what the tool hands you: pane IDs or live agent names in the TUI, `tN` addresses in hc
mode. Your own address is in an environment variable.

**Use addresses that do not change hands on long delegations.** A name follows the current occupant
of a pane, so it is released when they finish and another agent can take it over. Hold a reply
address as a name, send much later, and **the result lands in an unrelated session** — in the TUI,
cutting the turn that session was in with `esc`. If the `reply` in the tag you received is a name and
a good while has passed, check that it is the same target before sending. The reasoning is in
[targeting.md](targeting.md). In hc mode never use a name at all.

Carry **addresses only** in the tag. How to reply and what the status codes mean live in these
documents. Hauling the same explanation along with every request only eats the receiver's context.

## Getting the receiving side to read the contract

This protocol runs **only when the receiving side also knows the contract.** If they see the tag and
do not load this skill, they work without knowing how to reply and the result simply disappears.

That is why this skill's `description` makes a message beginning with an angle-bracket `herdr` tag
its highest-priority trigger. **Receiving the tag is sufficient** — trigger evaluation confirmed that
a session given nothing but the tag loads this skill. So **do not put "load this skill" ahead of it.**

Putting it ahead costs you something. That instruction consumes the other side's entire first turn,
and in the TUI `agent start` does not return until that turn ends, which adds a round trip before you
can send the request. It also leaves a sentence unrelated to the work on the screen the person is
watching. That is the price of asking twice for what the tag already does.

A failed trigger is silent. The requester simply gets no reply, and the cause does not surface. If you
suspect it, look at the other side's status and screen first.
