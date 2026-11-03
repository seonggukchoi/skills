# hc mode

herdr also ships as a desktop app built on **herdr-core**. There, agents talk to each other through
the `hc` CLI, not `herdr`. You are in hc mode when `$HC_TERMINAL_ID` is set; that value is your own
address.

**hc has its own manual.** `hc --skill` prints it, and `hc <command> --help` gives exact arguments.
This document does not copy that syntax. It covers only **how this skill's judgment and delegation
contract sit on top of hc**: what to take from hc as-is, what to add, and which TUI rules turn around.

Measured behavior below was observed with hc 0.1.17 and Claude Code agents. Anything not measured is
marked as such.

## 1. What hc already does: use it, do not rebuild it

| hc gives you | So in hc mode |
|---|---|
| **A sender tag.** A message an agent sends with `hc send` arrives wrapped as `<hc from="t4 cb">…</hc>`: address, then name | Do not put `to`, `from`, or `reply` in your own tag. The address lives in one place |
| **Parent and child.** Terminals you `hc run` are your children; `hc get` shows a terminal's `parent` | A single child doing a single task needs no thread id. The pairing is already there |
| **Notes about children.** hc types a note into the parent when a child's turn ends, it blocks, hits an error, or exits, e.g. `<hc>t9 cg exited (exit 3). Read: hc read t9</hc>` | Do not ask a child to report "I am stuck on a dialog". hc reports what the child cannot |
| **Blocked protection.** `hc send` to a `blocked` terminal is refused unless forced | Never force it. A blocked agent is waiting on a person, as in the TUI |
| **`hc wait --children`.** Returns on a child's news, or when a message reaches you | Use it instead of sleeping or polling (section 3) |

Where the tag appears, measured:

| How the text was sent | What the receiver sees |
|---|---|
| `hc send` from an agent (to a child, to a parent, or to an unrelated terminal) | `<hc from="tN name">` around the text, no `reach` |
| `hc send` from a terminal that reports no agent status, such as a plain shell | no `<hc>` tag at all |
| First task given as the `hc run` argument to an agent | no `<hc>` tag at all |
| First task given through an `hc run` template | `<hc from="tN name" reach="hc send tN when done or stuck">`, then the template body, then the task |

`reach` was seen only on that last row. Whether other cases (for example another machine) add it is
**not confirmed**. Do not rely on its presence; section 2 says where the reply address comes from.

## 2. What this skill adds on top of hc

hc ties a child to its parent. It has no notion of **a request id, a branch count, a delegation
depth, or a reply status**, so work spread across several agents, or handed on, loses track of
which answer belongs to which question. That part is this skill's contract, carried in a `herdr`
tag **without addresses**.

```
<herdr id="r7f3a2" hop="1" fanout="3">
Review the changes in the current working tree and tell me only what actually needs fixing.
</herdr>
```

When an agent sends that with `hc send`, the receiver sees the two tags on one line (measured):

```
<hc from="t4 lead"><herdr id="r7f3a2" hop="1" fanout="3">
Review the changes in the current working tree and tell me only what actually needs fixing.
</herdr></hc>
```

`id`, `hop`, `fanout`, and `status` mean exactly what `protocol.md` says. Read its sections on the
reply obligation, on not synthesizing before every reply is in, and on long chains; they hold
unchanged. Whether to delegate, who to pick, and how to word the request are in `delegation.md`,
also unchanged. Use `hc ls` and `hc get` where it says `agent list` and `agent get`, and drop
`$HC_TERMINAL_ID` from the roster, since `hc ls` lists every live terminal including you.

### Where the reply goes

1. **`reply` inside the `herdr` tag**, if present. It appears only on a handover (below).
2. Otherwise **the address in the enclosing `<hc from="…">`**: the `tN` part, not the name.
3. No `<hc>` tag at all (your first task came as the `hc run` argument): **your parent**, the
   `parent` field of `hc get "$HC_TERMINAL_ID"`.
4. None of these: you cannot tell who asked. Say so to the user instead of guessing.

**Reply to the address, never the name.** A name belongs to whichever live terminal holds it. Once
the requester ends, its name resolves to nothing, and as soon as another terminal takes that name a
send by name lands there (measured). Addresses were not reused in the same session (measured).

```
<herdr res="r7f3a2" status="ok" fanout="3">
Two places. A missing expiry check in the auth middleware, and the exit condition of the retry loop.
</herdr>
```

Send it with `hc send <address>` and a heredoc-built body, as in `protocol.md`, so apostrophes in the
body do not break the command. For long results, write a file and send its path. Check the result
of the send: a refusal means **the reply did not go through** (`blocked`: the requester is waiting on
a person, so tell the user and send after that; `finished`: the requester is gone, so tell the user
where the result is).

**Handover.** When you pass work to a colleague who should answer the original requester directly,
the requester is not in the colleague's `<hc from>`, so this is the one case that carries an address:
keep the original `id`, raise `hop`, and add `reply="<requester address>"`. Then send the requester a
`partial` saying you handed it over, as `protocol.md` describes.

**Simple case.** One child, one task, result back to you: the tag may be left out. hc's parent and
child pairing ties the answer to the question, and hc's notes cover the child failing to answer. Ask
the child in the task text to report with `hc send` to your address when done or stuck. Use the tag
as soon as there is a second branch, a handover, or a requester other than the parent.

**Starting more agents.** hc's manual says children do not start agents unless explicitly assigned.
Keep that: re-delegating to a new agent needs the request to allow it, and `hop` still stops at 3.
Asking a terminal that is already running is a message, not a new agent.

## 3. TUI rules that turn around in hc mode

| TUI rule | In hc mode | Why |
|---|---|---|
| Put nothing in the startup arguments; send the tag afterwards with `agent prompt` (rule 7) | **Put the first task, tag included, in the `hc run` argument** | hc's manual says a send to a booting agent can be dropped. The argument reaches the agent intact, angle brackets and newlines included (measured), so the tag fits. Check that the launch reports the first message as sent; if not, read the screen before sending anything, and do not resend blindly |
| Do not hold your turn with `agent prompt --wait` or `agent wait` | **`hc wait --children` is allowed** when your next step needs the replies | It returns when a message reaches you, so a person's instruction or another request is not shut out. A timeout is a check-in, not a failure. Still never sleep-and-poll |
| Insert a reply by sending `esc` to cut the requester's turn | **Do not.** Send the reply with `hc send`; do not use `hc interrupt` to make room for it | Measured with Claude Code: a message sent while it was `working` was queued and fed into the running turn at the next tool-call boundary. Other agents were not measured. The `interrupted` attribute is not used |
| Peers live as long as their pane | **A peer meant to stay needs `--outlive-parent`** | Without it a child ends when its parent's program ends (measured). With it, the child still sends its notes to the parent while the parent lives, and keeps the ended parent's address afterwards; sends to that address are refused as `finished` (measured) |

Two TUI rules still hold as written:

- **A dialog on someone else's screen is a question to a person** (rule 5). hc's manual mentions
  answering a trust dialog with keys; do that only when the person told you to. Otherwise report
  what the screen shows.
- **Clean up only what you started** (rule 8): `hc kill` then `hc rm`, on terminals you launched.

## What hc does not cover

hc runs terminals; it does not arrange windows. Requests about splitting or placing panes on screen
belong to the app's own tooling (hc's manual points to it). The judgment in `layout.md` (translate
the direction the person said, verify after acting, never steal focus) applies to whatever tool does
the arranging.
