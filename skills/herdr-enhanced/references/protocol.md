# The protocol that ties requests to replies

herdr gives you **a way to speak** to an agent in another pane, but no scheme for tying that
conversation into requests and replies. `agent prompt --wait` blocks synchronously, so there is no
path for handing off long work and carrying on with your own. This document fills that gap.

Do not rebuild what herdr already solved. Text injection and submission are handled atomically by
`agent prompt`, and the other side's state is recognized by herdr. **All that is defined here is the
contract for the text exchanged.**

## The tag

**The opening tag is the first line, the body follows, and the closing tag is the last line.** All
attributes go on the single opening-tag line; never wrap it.

```
<herdr id="r7f3a2" to="reviewer" from="w1:p1" reply="w1:p1" hop="1">
Review the changes in the current working tree and tell me only what actually needs fixing.
</herdr>
```

When splitting the same item across several places, carry the branch count too. The receiving side
echoes it back in its reply, so the requester learns **how many more are coming** from the reply
itself.

```
<herdr id="r7f3a2" to="reviewer" from="w1:p1" reply="w1:p1" hop="1" fanout="3">
Review the changes in the current working tree and tell me only what actually needs fixing.
</herdr>
```

```
<herdr res="r7f3a2" from="reviewer" to="w1:p1" status="ok" fanout="3">
Two places. A missing expiry check in the auth middleware, and the exit condition of the retry loop.
</herdr>
```

The closing tag is **the device that marks where the body ends.** Several replies arriving back to
back and read in one turn, or a person copying text off the screen with surrounding text mixed in,
still leave the boundary intact.

If you must show the shape of this tag inside a body, **drop the angle brackets and write the name
alone, or describe it in words.** Written verbatim, that line reads as the end of the body.

| Attribute | Meaning |
|---|---|
| `id` | The thread tying request to reply. Copy the same value into `res` when replying |
| `to` | The recipient. **That is, your own address as the reader of this tag.** Use this value when re-delegating or naming a reply address for a third party |
| `from` | The sender |
| `reply` | **Where to send the reply.** Usually the same as `from`, but a third party when the work was handed over. Reply to this value, not to `from` |
| `hop` | Depth in the delegation chain. Add one to the value received when passing a request on. **Above 3, do not pass it on** |
| `status` | Replies only. One of `ok`, `failed`, `partial` |
| `fanout` | **How many branches the same item was spread across.** Carried when a requester divides work among several, and the receiving side **echoes the value back in its reply** — the requester has to know how many more are pending in order to hold off synthesis |
| `interrupted` | Replies only. A marker that **the other side's in-progress turn was cut** to insert this reply |

Addresses are **live agent names or pane IDs.** Your own address is in an environment variable.

**Use pane IDs on long delegations.** A name follows the current occupant of a pane, so it is
released when they finish and another agent can take it over. Hold a reply address as a name, send
much later, and **the result lands in an unrelated session**, where the reply block above cuts the
turn that session was in with `esc`. If the `reply` in the tag you received is a name and a good
while has passed, check with `agent get` that it is the same target before sending. The reasoning is
in `targeting.md`.

```bash
echo "$HERDR_PANE_ID"
herdr agent list
```

Carry **addresses only** in the tag. How to reply and what the status codes mean live in this
document. Hauling the same explanation along with every request only eats the receiver's context.

## A tag can only be sent with `agent prompt`

**What makes something a delegation is what you sent, not which command you used.** If the recipient
is an agent and the text you sent contains work to do, it is a delegation regardless of which
argument carried it. `pane run` is the same — run a command against a pane with an agent up and that
text goes into their input box, not into a shell.

The place this distinction collapses most often is **`agent start`'s startup arguments.** Putting the
first instruction in while starting a new session looks like finishing in one step, and the sentence
reads as "a note attached at startup" rather than a request. But the moment you write there what to
read and what to tidy, it is **a delegation with no tag**, and the receiving side works with nowhere
to reply. A session that went out that way loaded this skill, read this very document, and still did
not reply — because the text it received had no `id` and no `reply`.

**Startup arguments cannot even carry a tag.** herdr composes those arguments into a command line for
the target shell, so angle brackets and newlines are rejected before execution (measured).

```
{"error":{"code":"invalid_agent_argument","message":"agent arguments cannot be encoded safely for the target shell"}}
```

This error is **a signal to change route, not to retry.** The same arguments will always produce the
same result.

So delegating to someone you are starting fresh **splits into two steps.**

```bash
# 1) Start it. Put nothing in the startup arguments.
herdr agent start <name> --kind <kind> --pane <pane id>

# 2) Send the request as a tag once it is up. The tag itself invokes the protocol, so there is
#    nothing to send ahead of it.
req=$(cat <<'EOF'
<herdr id="<request id>" to="<name>" from="<my address>" reply="<my address>" hop="1">
Write the work to be done here.
</herdr>
EOF
)
herdr agent prompt <name> "$req"
```

**Every attempt to collapse those two steps into one is what this section exists to stop.** Finish it
with a single line of startup argument and the reply vanishes wholesale, and that loss surfaces only
after the other side has done all the work.

**An agent may already be up even when the startup arguments end in an error.** The encoding
rejection happens after startup, so calling `agent start` again returns `agent_name_taken` this time.
When that happens, do not start fresh under a different name — look at that pane's state with
`agent get` and `agent read`, then move to step 2.

## Replying is an obligation

Once you receive a request, **reply under all circumstances.** The requester holds that work open
until a reply arrives, and with no reply they wait forever.

```bash
herdr agent prompt <reply value> '<herdr res="r7f3a2" from="reviewer" to="w1:p1" status="ok" fanout="3">
Two places. A missing expiry check in the auth middleware, and the exit condition of the retry loop.
</herdr>'
```

| Outcome | `status` | When |
|---|---|---|
| Done | `ok` | You finished what was asked |
| Failed or impossible | `failed` | You could not. **Include the reason** — the requester can find another route |
| In progress | `partial` | It will take a while. Report that you started and the expected duration first, then send `ok` when done |

**Silence is the worst outcome.** Failures get a reply too.

**Process and reply even to a malformed tag.** Discard a message because a closing tag was missing or
one attribute was absent, and the sender waits without knowing why. Work from as much as you can
read, and note what was missing in your reply so they fix it next time.

Once you receive a reply (`res`), **it ends there.** Reply to a reply and you start a ping-pong.
`reply` and `hop` are absent from reply tags because a reply is the terminus.

You may receive a `res` for something you never sent. That happens when another side handed work over
and named you as the reply address. Do not discard it as unfamiliar; use `from` to pick up the
context.

## Replies go in by cutting the other side's turn

Send a reply plainly while the requester is working and it queues, so the requester finishes that
turn **knowing only the replies that arrived earlier** and reads yours afterwards. On a request
spread across several places, that delay becomes pure loss — a reply that overturns the conclusion
arrives after the work has already set, and it has to be undone or redone from scratch.

**So never use `herdr agent prompt` on its own for a reply.** Called alone it just stacks onto the
queue without looking at whether the other side is working. Use the block below instead — fill in
`reply` and `body` and it handles the status query, the interrupt, the confirmation, the marker
correction, and the send in one go.

```bash
reply=reviewer          # the tag's reply value. if it is a name, the owner may have changed since (see below)
body=$(cat <<'EOF'
<herdr res="<id from the tag received>" from="<my address>" to="<reply value>" status="ok" fanout="<echo the value received>" interrupted="1">
Two places. A missing expiry check in the auth middleware, and the exit condition of the retry loop.
</herdr>
EOF
)

# Read the status. "could not query" and "not working" are different conclusions, so keep them apart.
status=$(herdr agent get "$reply" 2>/dev/null \
  | python3 -c 'import sys, json; print(json.load(sys.stdin)["result"]["agent"]["agent_status"])' 2>/dev/null)

case "$status" in
  working)
    herdr agent send-keys "$reply" esc
    herdr agent wait "$reply" --timeout 3000 >/dev/null 2>&1 \
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

herdr agent prompt "$reply" "$body" \
  || echo "the send was rejected. the reply did not go through — check the state again and decide what to do." >&2
```

**Skip this procedure and usually no error appears at all.** The reply stacks onto the queue and the
other side does read it eventually. So it looks fine, and the loss surfaces only after the requester
has done wasted work.

**It is a different story when the other side is `blocked`.** There, `agent prompt` is rejected with
`agent_blocked` and **not one character gets in.** Fail to check whether the send succeeded and you
will report a reply as delivered when it was not — which is the silence this document calls the worst
outcome. That is why the judgment is not left to a person's hands: run the block above as written.

Spelled out, the judgments the block makes are these.

- **Interrupt only when `working`.** There is nothing to interrupt in `idle`.
- **When `blocked`, stop without sending.** They are waiting on a person's answer, so interrupting
  makes that question disappear, and sending anyway is rejected by herdr. Tell the user, and send
  again after that answer is handled.
- **Failing to read the status is not the same as not being `working`.** Blur a failed query into
  "not working" and you stack onto the queue of someone you should have interrupted. If you could not
  confirm, note that in the reply body — the same rule as "Distinguish having sent from having been
  received" below.
- **Send `esc` only once.** Pressing it twice in Claude Code enters the edit mode that rewinds to the
  previous message, turning an interrupt into an operation that changes screen state.
- **`interrupted` marks "an interrupt was attempted", not "an interrupt happened".** Called without
  `--until`, `agent wait` matches any of `idle`, `done`, or `blocked` (measured), so it also reads as
  success when the other side finishes its turn **on its own** within those three seconds. herdr has
  no way to tell the two apart. So do not hang a judgment on this marker alone — what the receiving
  side should base its continuation on is in "Do not synthesize before every reply is in".
- **`agent wait` belongs here.** What is prohibited below is `agent prompt --wait` (holding your turn
  while waiting for a reply); this is a **check on whether the interrupt landed**, capped at three
  seconds, which is a different thing.
- **Copy tag values across verbatim.** `res` is the `id` you received, `to` is the `reply` you
  received, and `fanout` echoes the value you received. Do not wrap the body in single quotes; use a
  heredoc as above — replies commonly contain apostrophes, which close the quote right there and
  break the whole command.

**Do not interrupt requests (`id` tags).** New work is right to process in order, and there is no
grounds for cutting into what someone else is doing. The only thing you interrupt is a reply the
other side was holding work open for.

### What herdr cannot determine

**You cannot tell whether a person was about to step into that pane.** `agent get` has no field for a
person's keystrokes, and `focused` means only "that pane is selected on screen", not that someone is
typing. So the block above also interrupts work a person was watching.

The `working` condition screens some of this out — if a person is typing into the input box, that
agent has not started work and is not `working`. But **the moment a person moves to intervene while
work is running** is indistinguishable. If you know that pane matters to a person, do not interrupt:
send the reply as-is and add one line to the reply body about why you did not interrupt.

## Do not synthesize before every reply is in

Interrupting is only half of it. It is better **not to start work that would need interrupting.**

When spreading work, carry the branch count as `fanout` in the request tag, and the receiving side
echoes that value back in its reply. herdr keeps no central record of who is waiting on what, so
**the requester's own conversation context is the only ledger.** The branch count in the tag supports
that ledger.

When one reply arrives:

| Situation | What to do |
|---|---|
| Fewer replies received than the `fanout` value | **Do not start synthesis, judgment, or implementation.** Note what arrived in one line, write down what you are still waiting on, and end the turn |
| This is the last reply | Combine what you have and proceed |
| It carries `interrupted="1"` | The sender **attempted an interrupt**. herdr cannot tell whether it actually landed, so do not read this marker as a conclusion — **check the conversation directly just above** for what was stopped mid-flight and continue from there. If it was already finished, do not redo it |

Work unrelated to the replies is fine while waiting. All that is blocked is settling **a judgment that
hangs on the replies** ahead of time.

## End your turn after delegating

Once you have sent a request, **do not poll while waiting for the reply.** Leave one line about what
you are waiting on and end the turn. The reply arrives later as a new message, and why you asked is
still right there in the conversation.

Blocking stops the person's instructions and other sides' requests along with it.

For the same reason, **do not use `agent prompt --wait` in this protocol.** That option is for short
work whose result you take now and use immediately. When handing off long work, send the request and
step back.

**The official `herdr` skill recommends `--wait` as the default ("For normal agent work, `--wait` is
enough"). That recommendation holds only outside this protocol** — it assumes a short operation that
finishes in one go. For delegation and replies, this takes precedence. When reading both skills
together and they conflict, follow this rule.

The same holds when spreading work to several places at once. They will not arrive in order, but `id`
tells you which request each answers.

## Distinguish having sent from having been received

`agent prompt` succeeding means **the text was delivered to the other side**, not that they read it
and started processing. If they were working, it queues and gets consumed later.

There is an incident that blurred the two. A send to a target whose status could not be queried was
taken as receipt, the safety net was removed, and **the replies to a delegation spread across several
branches all evaporated.** The work was all done and only the results were gone, so from the sending
side it looked as though the delegation itself had never happened.

- Check the status where you can. Use `agent get` to see whether they moved.
- **Where you cannot check, record that you cannot.** Do not promote having sent into having been
  received.
- Do not resend immediately because a check failed. That produces a duplicate submission. See
  `pitfalls.md`.

## When the chain grows long

If work you took on **needs another pane, speak to that pane directly.** Bouncing "please ask them"
back to the requester turns them into a relay, doubling the round trips and wearing down context in
the retelling.

| Situation | How to send | Reply flow |
|---|---|---|
| **Supporting query** — you need the answer to synthesize | Request with `hop` raised by one | colleague → you → requester |
| **Handover** — they are the right one to finish it | Raise `hop` by one and set `reply` to the original requester | colleague → **straight to the requester** |

**Keep the original request's `id` even when handing over.** The requester can only tell which request
an answer belongs to by the `id` they sent. Mint a new `id` while handing over and **an answer they
have never seen** arrives, leaving the open request unclosable. The earlier note that "you may receive
a `res` for something you never sent" is about **a third party merely named as the reply address**;
what goes to the original requester is always the `id` they sent.

After handing over, **tell the requester with a `partial` that you did so.** Without that, the
requester stalls waiting on your reply.

`hop` is judged on **the value after adding one.** Received 3 means the raised value is 4, so it is
not passed on. A chain that long is a signal that the request's scope was drawn wrong, so reply to
the requester with that fact instead of passing it on.

**Include the collaboration record in your reply.** Write who you exchanged what with and what came of
it. The requester is not relaying, but they need to know what happened to make the next call.
Otherwise they will order the same investigation again.

## Getting the receiving side to read this document

This protocol runs **only when the receiving side also knows the contract.** If they see the tag and
do not load this skill, they work without knowing how to reply and the result simply disappears.

That is why this skill's `description` makes a message beginning with an angle-bracket `herdr` tag
its highest-priority trigger. **Receiving the tag is sufficient** — trigger evaluation confirmed that
a session given nothing but the tag loads this skill. So **do not put "load this skill" ahead of it in
the startup arguments.**

Putting it ahead costs you something. That instruction consumes the other side's entire first turn,
and since `agent start` does not return until that turn ends, it adds a round trip before you can send
the request. It also leaves a sentence unrelated to the work on the screen the person is watching.
That is the price of asking twice for what the tag already does.

A failed trigger is silent. The requester simply gets no reply, and the cause does not surface. If you
suspect it, look at the other side's status and screen first.
