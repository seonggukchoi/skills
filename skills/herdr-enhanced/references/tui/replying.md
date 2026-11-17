# Replying with the herdr CLI

The reply obligation, status codes, why a reply has to reach a busy requester, and checking every
send are in [common/protocol-replying.md](../common/protocol-replying.md). This file is how herdr
does it: by cutting the requester's turn.

## Replies go in by cutting the other side's turn

Send a reply plainly while the requester is working and it queues, so the requester finishes that
turn without it. **So never use `herdr agent prompt` on its own for a reply.** Called alone it
just stacks onto the queue without looking at whether the other side is working. Use the block below
instead — fill in `reply_to` and `body` and it handles the status query, the interrupt, the
confirmation, the marker correction, and the send in one go.

```bash
reply_to=reviewer       # the tag's reply value. if it is a name, the owner may have changed since (see below)
body=$(cat <<'EOF'
<herdr res="<id from the tag received>" from="<my address>" to="<reply value>" status="ok" fanout="<echo the value received>" interrupted="1">
Two places. A missing expiry check in the auth middleware, and the exit condition of the retry loop.
</herdr>
EOF
)

# Read the status. "could not query" and "not working" are different conclusions, so keep them apart.
agent_status=$(herdr agent get "$reply_to" 2>/dev/null \
  | python3 -c 'import sys, json; print(json.load(sys.stdin)["result"]["agent"]["agent_status"])' 2>/dev/null)

case "$agent_status" in
  working)
    herdr agent send-keys "$reply_to" esc
    herdr agent wait "$reply_to" --timeout 3000 >/dev/null 2>&1 \
      || body="${body/ interrupted=\"1\"/}" ;;
  blocked)
    # in this state agent prompt is rejected with agent_blocked — not one character gets in.
    echo "the reply target is waiting on a person's answer; cannot send now. tell the user." >&2
    exit 1 ;;
  "")
    echo "could not read the status. send without interrupting, and note in the reply body that it is unverified." >&2
    body="${body/ interrupted=\"1\"/}" ;;
  *)
    body="${body/ interrupted=\"1\"/}" ;;
esac

herdr agent prompt "$reply_to" "$body" \
  || echo "the send was rejected. the reply did not go through — check the state again and decide what to do." >&2
```

**Skip this procedure and usually no error appears at all.** The reply stacks onto the queue and the
other side does read it eventually. So it looks fine, and the loss surfaces only after the requester
has done wasted work.

**It is a different story when the other side is `blocked`.** There, `agent prompt` is rejected with
`agent_blocked` and **not one character gets in.** That is why the judgment is not left to a
person's hands: run the block above as written.

Spelled out, the judgments the block makes are these.

- **Interrupt only when `working`.** There is nothing to interrupt in `idle`.
- **When `blocked`, stop without sending.** Tell the user, and send again after that answer is
  handled.
- **Failing to read the status is not the same as not being `working`.** Blur a failed query into
  "not working" and you stack onto the queue of someone you should have interrupted. If you could not
  confirm, note that in the reply body.
- **Send `esc` only once.** Pressing it twice in Claude Code enters the edit mode that rewinds to the
  previous message, turning an interrupt into an operation that changes screen state.
- **`interrupted` marks "an interrupt was attempted", not "an interrupt happened".** Called without
  `--until`, `agent wait` matches any of `idle`, `done`, or `blocked` (measured), so it also reads as
  success when the other side finishes its turn **on its own** within those three seconds. herdr has
  no way to tell the two apart. So do not hang a judgment on this marker alone.
- **`agent wait` belongs here.** What is prohibited for delegation is `agent prompt --wait` (holding
  your turn while waiting for a reply); this is a **check on whether the interrupt landed**, capped
  at three seconds, which is a different thing.
- **A name in `reply` may have changed hands.** Held as a name and sent much later, the reply lands
  in an unrelated session and cuts *its* turn with `esc`. If a good while has passed, check with
  `agent get` that it is the same target before sending.

## What herdr cannot determine

**You cannot tell whether a person was about to step into that pane.** `agent get` has no field for a
person's keystrokes, and `focused` means only "that pane is selected on screen", not that someone is
typing. So the block above also interrupts work a person was watching.

The `working` condition screens some of this out — if a person is typing into the input box, that
agent has not started work and is not `working`. But **the moment a person moves to intervene while
work is running** is indistinguishable. If you know that pane matters to a person, do not interrupt:
send the reply as-is and add one line to the reply body about why you did not interrupt.

## When a reply cut your turn

On the requester's side: a reply carrying `interrupted="1"`, or a tool call just above it showing as
rejected or interrupted, means the sender **tried to cut your turn with `esc`**; herdr cannot tell
whether it landed. An agent cut by `esc` may show its in-flight tool call as refused or interrupted by
the user, but that came from the reply, so **do not stop**: check the conversation directly above for
what was cut off, rerun it, and continue. If it was already finished, do not redo it. The same holds
without the marker, which is dropped when the interrupt could not be confirmed. A person pressing
`esc` at that moment looks the same, so **ask the user before rerunning anything hard to undo.**

Then apply the `fanout` rule in [common/protocol-waiting.md](../common/protocol-waiting.md) as usual.
