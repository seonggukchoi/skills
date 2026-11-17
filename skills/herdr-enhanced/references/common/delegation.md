# Deciding what to delegate, and working together

What to hand off, who to hand it to, and how to word it. The wire format is in
[protocol-tag.md](protocol-tag.md) — **read that before you send.** Send plain prose with no envelope
and the receiving side has nowhere to reply to, and that failure is silent.

How to carry it out:
[tui/delegating.md](../tui/delegating.md) (building the roster with `agent list`, starting a peer in
three steps, why not `--wait`) ·
[app/delegating.md](../app/delegating.md) (what hc already does, `hc ls`, the first request in the
`hc run` argument, `hc wait --children`, `--outlive-parent`).

## What makes it a delegation

**What makes something a delegation is the text you send, not the command you use.** If the
recipient is an agent and the text contains work to do, it is a delegation, whatever argument
carried it — including the arguments of the command that launches the agent, and a command run into
a pane where an agent is up (that text goes into their input box, not into a shell).

So **a new peer's first work arrives as a tagged request, never as an untagged line of work.** Each
CLI carries it differently: the TUI cannot fit a tag into launch arguments, so the tag goes in after
launch; hc puts the tag in the launch argument itself. Neither lets a plain sentence of work through.

## Do it yourself, or delegate?

**Anything that finishes in one turn, a simple lookup, or work that fits inside your own context:
just do it yourself.** Delegation costs a round trip and burns the other side's context too.

Delegation pays off in three cases.

- Long work that needs to run **in parallel**.
- **A pane that already knows** that repository or domain. No context to rebuild.
- Work the person needs to **watch or step into in real time**.

## Pane work versus subagent work

The fork is **whether what you hand off is disposable or a colleague who stays.**

| This skill (panes) | Subagents (Task) |
|---|---|
| The person must be able to watch and intervene on screen | The person does not need to see it |
| Left running long, results checked later | Results taken now and used immediately |
| The pane stays, carrying context forward | Fine for it to vanish when done |
| Names a specific target that is already up | Created fresh for the purpose |

"Find one and hand it to them if there is one" cannot be expressed with subagents at all, because it
means finding something that already exists.

## Look at real state before picking a target

When the user names a specific target, **query first rather than creating one arbitrarily.**

**The list includes you.** The listing does not filter out the calling pane (measured in the TUI: one
of nine entries was the caller; `hc ls` lists every live terminal including you). Delegate to the
list as-is and **you send to yourself**, whose tag re-triggers this skill and starts the same work
over. Drop your own address when building the roster.

**Do not narrow the scope when enumerating everything.** A target you did not send to is a silent
omission (see below).

| Status | What to do |
|---|---|
| `idle` | Delegate straight away |
| `done` | An unacknowledged result is sitting there. **Read it first**, then decide whether to build on it or start something new |
| `working` | It will queue, but tell the user first if it looks like a long wait |
| `blocked` | Waiting on a person's answer. **Do not stack a new request** — it gets absorbed as the answer to the question and disappears. Read what is being asked first |
| `unknown` | Alive but unclassified. You can send, but **you cannot confirm it started.** Record that it is unconfirmable |
| Not in the list | The user said "if there is one", so report that there is not, and ask whether to create one. **Creating one silently defies the expectation** |

Running an ordinary command in an empty shell pane with no agent is not delegation. That path
belongs to the official `herdr` skill (TUI) or `hc --skill` (hc mode).

## Word the request so nobody has to ask back

A vague delegation makes the receiving side **put up a choice and stop, waiting for a person's
answer.** Messages arriving meanwhile get absorbed as the answer to that question and disappear, the
requester never gets a reply, and the whole chain stalls. This shows up as `blocked`.

A request carries **what, where, and in what form to answer.** Points where judgment could diverge
are settled by the requester before handing over.

- Bad: `run the tests for me`
- Good: `run only the unit tests in this repository, and reply with the names of failing cases and
  the first line of each error`

## When you split work across several places

**Tell them about each other.** Word it like "A and B are on this too — talk to them directly if you
need to, and note in your reply what you exchanged." Without that, a colleague who does not know
others exist either shoulders it alone or asks the requester back.

**When someone joins mid-flight, tell the existing ones.** The roster you handed out was a snapshot
of that moment, so without an update the newcomer stays invisible to everyone.

**Put the branch count (`fanout`) in the request tag.** Replies arrive staggered, and starting your
synthesis on the first one freezes the conclusion before the rest land. The receiving side echoes
that value back in its reply, so every reply shows how many more are coming — the format is in
[protocol-tag.md](protocol-tag.md), and the rule for what to do once you have it is in
[protocol-waiting.md](protocol-waiting.md).

## Omissions in a batch delegation are silent

**A target you did not send to sends no reply, which is indistinguishable from "still working."**
There is an incident where an arbitrarily narrow scope dropped several items wholesale with no
signal at all.

Do not guess at targets: **enumerate them with a query and confirm** before sending. Keep the `id`s
so you can reconcile what you sent against what came back. **If the scope is ambiguous, ask rather
than narrow.**
