# Addresses and tags in hc mode

The tag and its attributes are in [common/protocol-tag.md](../common/protocol-tag.md), and the
targeting principles in [common/targeting.md](../common/targeting.md). **The contract does not change
in hc mode**; this file covers only the address values and how hc wraps the text.

## Addresses are `tN`

Write hc addresses (`tN`) wherever the contract puts an address: `to`, `from`, `reply`. Your own is
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
[common/protocol-chains.md](../common/protocol-chains.md) describes.

## A first request in the `hc run` argument leaves out `to`

A new peer's first request rides in the `hc run` argument ([delegating.md](delegating.md)), and its
`tN` does not exist until `hc run` returns. So **that one tag leaves `to` out.** Never fill it with a
guessed `tN` or a name: a wrong `to` is worse than none, because the receiver passes it on when
re-delegating. Every other tag, including later requests to the same peer with `hc send`, carries `to`
as usual.

```
<herdr id="r7f3a2" from="t4" reply="t4" hop="1" fanout="3">
Review the changes in the current working tree and tell me only what actually needs fixing.
</herdr>
```

**When a tag you receive has no `to`, read it as your own `$HC_TERMINAL_ID`.** `to` always means
the reader's own address, so the reader can always supply it. Use that value wherever the contract
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
