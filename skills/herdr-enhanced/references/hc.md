# hc mode

herdr also ships as a desktop app built on **herdr-core**. There, agents talk to each other through
the `hc` CLI, not `herdr`. You are in hc mode when `$HC_TERMINAL_ID` is set; that value is your own
address.

**hc has its own manual.** `hc --skill` prints it, and `hc <command> --help` gives exact arguments.
This document does not copy that syntax. It covers only **how this skill's judgment and delegation
contract run over hc**.

**The contract does not change in hc mode.** The tag, its attributes, the reply obligation, and the
synthesis rules are exactly those of `protocol.md`. Only two things differ: **the address values**,
and **the commands that carry the text**.

Measured behavior below was observed with hc 0.1.17 and Claude Code agents. Anything not measured is
marked as such.

## Addresses

Write hc addresses (`tN`) wherever `protocol.md` puts a pane ID: `to`, `from`, `reply`. Your own is
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
`protocol.md` describes.

### A first request in the `hc run` argument leaves out `to`

A new peer's first request rides in the `hc run` argument (below), and its `tN` does not exist until
`hc run` returns. So **that one tag leaves `to` out.** Never fill it with a guessed `tN` or a name:
a wrong `to` is worse than none, because the receiver passes it on when re-delegating. Every other
tag, including later requests to the same peer with `hc send`, carries `to` as usual.

```
<herdr id="r7f3a2" from="t4" reply="t4" hop="1" fanout="3">
Review the changes in the current working tree and tell me only what actually needs fixing.
</herdr>
```

**When a tag you receive has no `to`, read it as your own `$HC_TERMINAL_ID`.** `to` always means
the reader's own address, so the reader can always supply it. Use that value wherever `protocol.md`
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

## What hc already does: use it, do not rebuild it

| hc gives you | So in hc mode |
|---|---|
| **Parent and child.** Terminals you `hc run` are your children | They end when you end, unless started with `--outlive-parent` (below) |
| **Notes about children.** hc types a note into the parent when a child blocks, hits an error, or exits, e.g. `<hc>t9 cg exited (exit 3). Read: hc read t9</hc>` | Read that child's screen and decide about its work. Do not ask children to report "I am stuck on a dialog"; hc reports what they cannot |
| **Blocked protection.** `hc send` to a `blocked` terminal is refused unless forced | Never force it. A blocked agent is waiting on a person, as in the TUI |
| **`hc wait --children`.** Returns on a child's news, or when a message reaches you | Use it instead of sleeping or polling (below) |

Use `hc ls` and `hc get` where `delegation.md` says `agent list` and `agent get`, and drop
`$HC_TERMINAL_ID` from the roster, since `hc ls` lists every live terminal including you.

hc's manual says children do not start agents unless explicitly assigned. Keep that alongside `hop`:
re-delegating to a new agent needs the request to allow it.

## Same contract, different carrier

Each row keeps what the TUI rule protects; only the means of carrying it changes.

| What the contract requires | TUI carrier | hc carrier | Why hc differs |
|---|---|---|---|
| **A new peer's first work arrives as a tagged request**, never as an untagged line of work | Start with nothing in the `agent start` arguments, then send the tag with `agent prompt` | **Put the tagged request in the `hc run` argument**, without `to` (see Addresses) | hc's manual says a send to a booting agent can be dropped. The argument reaches the agent intact, angle brackets and newlines included (measured), so the tag fits. Only a template launch reports whether the first message was sent; without a template the response carries no such field, so read the screen if you are unsure, and do not resend blindly |
| **Waiting for replies must not shut out a person or other requests** | End the turn; no `agent prompt --wait`, no `agent wait` | **End the turn, or `hc wait --children`** when the next step needs the replies | `hc wait` returns when a message reaches you, so nobody is shut out. A timeout is a check-in, not a failure. Never sleep-and-poll |
| **A reply must reach a requester who is busy** | Cut the requester's turn with `esc`, then `agent prompt`, marking `interrupted` | **`hc send` the reply**; no `esc`, no `hc interrupt`, no `interrupted` attribute | Measured with Claude Code: a message sent while it was `working` was queued and fed into the running turn at the next tool-call boundary. Other agents were not measured |
| **A peer meant to stay outlives the work that started it** | Panes stay until closed | **Start it with `--outlive-parent`** | Without it a child ends when its parent's program ends (measured). With it, the child still sends notes to the parent while the parent lives, and keeps the ended parent's address afterwards; sends to that address are refused as `finished` (measured) |

Check every reply send. A refusal means **the reply did not go through**: `blocked` means the
requester is waiting on a person, so tell the user and send after that; `finished` means the
requester is gone, so tell the user where the result is. Build the body with a heredoc, as in
`protocol.md`, and for long results write a file and send its path.

Two TUI rules hold as written:

- **A dialog on someone else's screen is a question to a person** (rule 5). hc's manual mentions
  answering a trust dialog with keys; do that only when the person told you to. Otherwise report
  what the screen shows.
- **Clean up only what you started** (rule 8): `hc kill` then `hc rm`, on terminals you launched.

## Arranging panes: `scripts/app/hc-layout`

hc runs terminals; it does not arrange windows. **`scripts/app/hc-layout` does every arrangement this
skill needs, from any machine, without moving focus.** Use it instead of rebuilding the steps. It
lives in this skill's own directory (the base directory shown when the skill loads), wherever the
skill was installed.

```bash
L=<this skill's directory>/scripts/app/hc-layout
"$L" tree [space|tab|terminal ...] [--on M]       # the split tree: groups, direction, weights, ids
"$L" where "$HC_TERMINAL_ID"                       # the space, tab and pane holding a terminal
"$L" open --anchor <pane|terminal> --direction right|down|left|up [--ratio 6:4] [--cwd D] [-- CMD]
"$L" open --new-tab-in <space> [--name N] [--cwd D] [-- CMD]   # default CMD: the machine's shell
"$L" place <terminal> --anchor <pane|terminal> --direction D [--ratio A:B]  # running terminal there
"$L" resize <pane|terminal|group> --ratio 2:1[:1]  # that node and its siblings, in tree order
"$L" move-tab <tab> --to-space <space> [--index N] # same machine; tree, ids and sizes kept
"$L" adopt <terminal> --tab-of <terminal>          # add a running terminal at the end of a tab
```

Read ids from `tree` or `herdr-app ls`; another machine's ids carry a `machine/` prefix in the app,
and the script takes either form. `--ratio` on `open`/`place` is anchor:new and splits the share
the two held, so other siblings keep theirs. Every command prints JSON with the route it took
(`via`); `place` and `open` also report `verified` from reading the tree back (rule 3).

### Two routes, chosen automatically

| Route | When | How it changes the layout |
|---|---|---|
| `app` | `herdr-app status` works here (the computer with the Herdr window) | Public commands only. A placeholder pane is split where the terminal should go, the terminal joins the tab by labels and is swapped into the placeholder's slot, the placeholder closes. `layout.resize` sets sizes. Nothing takes focus |
| `doc` | No Herdr app here (a remote machine over ssh) | Writes that machine's layout document with `doc.set`: the shape is checked first (unknown shape: nothing is written), the write carries the version read (another client wrote first: read again and retry), and the edit follows what the app itself writes. Then `herdr.space`/`herdr.tab` labels are set, since the app does not relabel |

Every client (desktop, mobile, another computer) draws from the machine's layout document, so both
routes show the same everywhere. Measured with herdr-app 0.1.16 and hc 0.1.21: the app picked up
`doc` writes at once, kept them alongside its own commands, and refused a stale version with
`conflict`. Not measured: a write while no app is running (the app reads the document when it
starts), and the mobile app's screen. **Write the document only through the script's `doc` route**,
and only where no app is reachable: never with your own `doc.set`, and never with `--via doc` where
`herdr-app status` works. Reading it (`tree`, `where`) is fine anywhere.

If a newer Herdr stores the document differently, the script stops with "a shape this script does
not know" and changes nothing. Report that; do not work around it.

### Limits that hold on either route

- **A terminal belongs to its machine.** No tab or pane moves between machines; the script refuses.
- **Labels place only a terminal without a pane.** Relabelling a pane's terminal moves nothing
  (measured); moving one is `place` or `move-tab`.
- A labelled terminal with no app running and no `doc` write appears only when an app next starts.
  `hc run --bg --keep --label herdr.space=<id> --label herdr.tab=<id>` lands at the end of the
  tab's outermost split; with `herdr.space` only, as a new tab; with no labels, nowhere.
- A tab that is not shown reports default terminal sizes (120x40); judge sizes from `tree`.
- Weights are relative within one split; a missing weight counts as `1` (consistent with every
  measurement).

### Lifetimes and cleanup

- `open` starts terminals with `--no-parent --keep`, like the app's own: they outlive the agent
  that asked. A terminal you start yourself with `hc run` stays your child; add `--outlive-parent`
  if it should stay after you end.
- **Clean up only what you started.** The script removes its own placeholders
  (`sh -c 'while :; do sleep 3600; done'`); it never closes a pane it did not create.
