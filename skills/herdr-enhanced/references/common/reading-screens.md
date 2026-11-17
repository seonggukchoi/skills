# Reading another pane's screen

What follows is the kind where **a wrong answer comes out looking plausible.** No error is raised,
so you cannot catch it yourself, and knowing about it in advance is the only defense.

How to read state rather than screen text:
[tui/diagnosing.md](../tui/diagnosing.md) (`agent get`, `agent read --source detection`) ·
[app/delegating.md](../app/delegating.md) (`hc get`, hc's notes about blocked children).

## A sentence you read off a screen is not the user's words

When its input box is empty, Claude Code **draws suggestion text in that spot proposing what to do
next.** Read as plain text, it is character-for-character identical to something a person typed.

Knowing how suggestion text behaves lets you catch your own misreading.

- **It does not exist in the input buffer.** So sending Enter submits nothing.
- **Its content keeps changing.** As that pane's work advances, the suggestion refreshes. If the
  wording differs from a moment ago, the person did not edit it — the suggestion changed.
- **It is plausible.** Generated from that session's context, it reads exactly like "a sentence the
  user might have written." That is the most dangerous part.

There is an incident where suggestion text across several sessions was misread as "answers the user
typed but did not submit", and git operations were ordered on top of an approval that never
happened. Suggestions come out of that session's context, so they fit neatly against the decision a
person was waiting on. **The user had made no such decision.**

You do not have to judge this by eye. In the TUI, herdr recognizes agent status and gives a snapshot
made for detection; read the ANSI form only when color and emphasis are the basis for a decision
([tui/diagnosing.md](../tui/diagnosing.md)). In hc mode, read the status with `hc get` (no detection
snapshot is documented there). The principle holds either way: **never promote a sentence read off a screen into a user's decision.**
When you need approval, ask the user directly.

The reverse misreading also happens: in the TUI, a tool call shown as refused or interrupted right
before a reply tag was cut by that reply's `esc`, not refused by the user. See
[tui/replying.md](../tui/replying.md) ("When a reply cut your turn").

## A question still on screen does not mean an answer came back

The previous trap has another layer. Even when the sentence on screen **really was there and was not
suggestion text**, that does not make it an approval.

A question an agent put up is **something that agent asked a person**, not an answer a person gave.
If anything, the fact that the question is still on screen leans toward **no answer having
arrived** — had one come, that screen would already have moved on.

So when you get a request like "they were asking about something over there, go ahead with it",
check two things together.

- **Who asked.** If the sender of the question is an agent, that sentence is a request, not a
  decision.
- **Whether an answer exists.** If a person really answered, the trace shows up as a state change,
  not on screen. Look at whether `blocked` cleared and whether work advanced afterwards.

For anything hard to reverse or affecting other people, do not act on an unverified approval. Asking
the user directly costs far less than undoing a bad merge.

**A dialog on someone else's screen is a question to a person.** Do not answer it with keys on their
behalf unless the person told you to; report what the screen shows.
