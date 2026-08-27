# Traps in observation and judgment

What follows is the kind where **a wrong answer comes out looking plausible.** No error is raised,
so you cannot catch it yourself, and knowing about it in advance is the only defense.

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

In herdr you do not have to judge this by eye. There is status recognition and a dedicated snapshot.

```bash
herdr agent get <target>
herdr agent read <target> --source detection
```

Read the ANSI form only when color and emphasis are the basis for a decision. The principle holds
either way: **never promote a sentence read off a screen into a user's decision.** When you need
approval, ask the user directly.

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

## Something failing for no reason is a signal to recheck premises, not to route around

In the incident above, the moment Enter did not take twice was the moment to doubt the judgment.
Instead, a different route was taken and the incident completed itself.

**When a route fails for no reason, it does not mean find another way — it means a premise is
wrong.** In herdr this shows up in these shapes.

| Symptom | Premise to doubt |
|---|---|
| Agent startup ends in a timeout | Was that pane really an empty shell at a prompt |
| A prompt is rejected as stalled (`agent_prompt_stalled`) | **Is the other side really processing your text.** This error fires when a submission sent with `--wait` **has already been accepted** and the other side shows no state change within five seconds (measured: the official skill's condition). So **the text is already with them** — read it as a failure and resend, and you make them do the same work twice. Do not resend; check with `agent get` and `agent read` whether it was processed |
| Reading returns nothing | Is it the right target pane. Is it running on an alternate screen |
| A command landed on someone else's pane | Did an omitted target grab the focused pane |

## Do not narrow down to the environment by elimination

Crossing candidates off one at a time and then picking the most plausible survivor **produces an
answer with herdr missing from the candidate list.** This actually happened inside a herdr pane.

1. Multiplexer candidates were crossed off using environment variables.
2. A terminal-app variable was still set, so that app was concluded to be the host.
3. That app was driven to split "the current window" left/right and top/bottom. **The outer window
   the person was using got carved up.**

All three steps make sense individually and the conclusion is wrong. **The variables of the terminal
that launched the herdr server are inherited by every pane as-is.** On one macOS terminal,
`TERM_PROGRAM`, `TERM_PROGRAM_VERSION`, `ITERM_SESSION_ID`, `LC_TERMINAL`, and `TERMINFO_DIRS` all
carried the outer window's values (measured), and among them `ITERM_SESSION_ID` **addresses exactly
the window herdr was launched from**, so acting on it drives commands straight into someone else's
screen. On a different terminal the variable names change but the structure is the same.

- **Judge on positive evidence.** `HERDR_ENV` or `HERDR_PANE_ID` present means herdr. That judgment
  needs no elimination.
- **Terminal-app variables tell you only "what launched herdr."** They say nothing about where you
  are.
- **If you cannot reach a judgment, stop before touching the screen.** A screen split without
  knowing which environment you are in leaves the undo to a person.

`tty` does not help here either. Commands inside a pane usually report `not a tty`, so trying to
compare that against the outer window yields no conclusion.

## The command you called to verify gets read backwards

The very command called to verify a layout invites a misreading. Read backwards, **it convinces you
a wrong layout is right.**

| Command | Easy to read backwards as | What it actually means (measured) |
|---|---|---|
| `pane edges` | `right: true` meaning "there is a neighbor on the right" | **`true` means that side is an outer boundary.** With a neighbor it is `false` |
| `pane neighbor` | It succeeded, so there is a neighbor that way | It **succeeds with exit code 0 even with no neighbor.** The `neighbor_pane_id` key is simply absent |
| `pane split` response | The response is fine, so it split the way I asked | **The response carries no coordinates.** It cannot tell you whether the direction was right |

So verify layout with the coordinates from `pane layout`. The criteria are in `layout.md`.

## Do not promote circumstance into cause

**The better something fits a trap you know, the harder you should look for a counterexample.**
There is a case where exit times one second apart were read as "evidence one command killed several."
In fact a person had simply shut them down back to back.

In the same family: a symptom report can be accurate while **its attribution of cause is wrong.** The
value of a report is in the symptom observed, not the cause proposed. The receiving side re-verifies
the cause.

## Do not turn a failed confirmation straight into a resend

Sending a prompt and failing to confirm it started **is not the same as failing to send.** The text
may already be in the other side's input or queue. Resend as-is and you make them do the same work
twice.

Query the state first and see whether they already processed it.

```bash
herdr agent get <target>
herdr agent read <target> --source recent-unwrapped --lines 80
```

For the same reason, do not stack repeated wait commands just because no response came. What to wait
for is covered in `protocol.md`.

## Do not parse transcripts to find a target

Do not use the path of identifying sessions through `~/.claude/projects/**/*.jsonl`. Those files
**mix in secrets and personal data, so pulling them into context is itself risky**, and the result
is guesswork besides.

The source of truth for live targets is herdr.

```bash
herdr agent list
herdr pane list          # this is where you check the source of truth — narrowing with --workspace falsifies the conclusion that herdr does not know
herdr workspace list
```

Not here means herdr does not know about it. Do not fill the gap with a guess; ask which one.

## When reading shows nothing, look for the reason before raising the line count

If raising the line count still does not reveal a completed response, that pane's agent is **running
on an alternate screen.** Lines pushed off an alternate screen do not land in scrollback, so a bigger
line count recovers nothing.

At that point, have the agent write the full response to a file in a temporary directory and reply
with just the path, then read the file yourself. **This is a fallback after a failed read, so do not
demand file output in the initial prompt.**
