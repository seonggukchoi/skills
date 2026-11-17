# Delegating with the herdr CLI

Whether to delegate, choosing and wording, and the rule that the text you send makes it a delegation
are in [common/delegation.md](../common/delegation.md). The tag is in
[common/protocol-tag.md](../common/protocol-tag.md), and waiting in
[common/protocol-waiting.md](../common/protocol-waiting.md). This file is how herdr carries them.

## Building the roster

```bash
echo "$HERDR_PANE_ID"
herdr agent list
herdr pane list          # do not add --workspace
```

- **`agent list` includes you** (measured: one of nine entries was `$HERDR_PANE_ID`). Drop
  `$HERDR_PANE_ID` from the roster, or you send to yourself.
- **Do not add `--workspace` when enumerating everything.** That option narrows scope to the current
  workspace (measured: 2 of 10 returned). It is right when confirming membership
  ([targeting.md](targeting.md)), but here a target you did not send to is a silent omission.
- Read a target's status with `agent get`; read a `done` result or a `blocked` question with
  `agent read` before sending anything.

Running an ordinary command in an empty shell pane with no agent (`pane run`, `pane wait-output`)
belongs to the **official `herdr` skill** — read the syntax there rather than copying it here. But
`pane run` against a pane with an agent up puts that text into their input box, not into a shell, so
work sent that way is a delegation.

## A tag can only be sent with `agent prompt`

The place the delegation rule collapses most often is **`agent start`'s startup arguments.** Putting
the first instruction in while starting a new session looks like finishing in one step, and the
sentence reads as "a note attached at startup" rather than a request. But the moment you write there
what to read and what to tidy, it is **a delegation with no tag**, and the receiving side works with
nowhere to reply. A session that went out that way loaded this skill, read the protocol in full, and
still did not reply — because the text it received had no `id` and no `reply`.

**Startup arguments cannot even carry a tag.** herdr composes those arguments into a command line for
the target shell, so angle brackets and newlines are rejected before execution (measured).

```
{"error":{"code":"invalid_agent_argument","message":"agent arguments cannot be encoded safely for the target shell"}}
```

This error is **a signal to change route, not to retry.** The same arguments will always produce the
same result.

## Starting a new peer takes three steps

The middle one is a check, and it is the one that gets skipped — a startup that stops at a dialog
(folder trust, loading external content) looks finished from the caller's side.

```bash
# 1) Start it. Put nothing in the startup arguments.
herdr agent start <name> --kind <kind> --pane <pane id>

# 2) Look before sending. Startup can end at an approval dialog: `agent start` then returns
#    `agent_not_ready`, and the agent is up as `blocked` with `launch_pending` set (measured).
#    Send nothing until you have read the state.
agent_status=$(herdr agent get <name> 2>/dev/null \
  | python3 -c 'import sys, json; print(json.load(sys.stdin)["result"]["agent"]["agent_status"])' 2>/dev/null)
case "$agent_status" in
  idle) ;;                                   # ready — go on to step 3
  *)
    herdr agent read <name> --source recent-unwrapped --lines 40
    # A dialog on that screen is a question to a person. Do not answer it, do not push the request
    # through `pane run`, `pane send-text`, or `send-keys` — those bypass the blocked check, and
    # Enter confirms whatever option is highlighted. Report what is on screen and end the turn;
    # the delegation is pending, not sent.
    exit 1 ;;
esac

# 3) Send the request as a tag. The tag itself invokes the protocol, so there is nothing to send
#    ahead of it.
req=$(cat <<'EOF'
<herdr id="<request id>" to="<name>" from="<my address>" reply="<my address>" hop="1">
Write the work to be done here.
</herdr>
EOF
)
herdr agent prompt <name> "$req"
```

**Every attempt to collapse step 1 and step 3 into one is what this section exists to stop.** Finish it
with a single line of startup argument and the reply vanishes wholesale, and that loss surfaces only
after the other side has done all the work.

**An agent may already be up even when the startup arguments end in an error.** The encoding
rejection happens after startup, so calling `agent start` again returns `agent_name_taken` this time.
When that happens, do not start fresh under a different name — look at that pane's state with
`agent get` and `agent read` (step 2), then move to step 3.

## Do not hold your turn waiting

After sending, end the turn. Use neither `agent prompt --wait` nor `agent wait` to wait for a reply;
both block the person's instructions and other panes' requests.

**The official `herdr` skill recommends `--wait` as the default ("For normal agent work, `--wait` is
enough"). That recommendation holds only outside this protocol** — it assumes a short operation that
finishes in one go, whose result you take now and use immediately. For delegation and replies, this
takes precedence. When reading both skills together and they conflict, follow this rule.

The one place `agent wait` belongs is the reply block in [replying.md](replying.md): a three-second
check on whether an interrupt landed, which is a different thing from waiting for a reply.

`agent prompt` succeeding means the text was delivered, not that they started a turn (the official
skill says the same). Check with `agent get` whether they moved.
