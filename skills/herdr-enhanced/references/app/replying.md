# Replying with hc

The reply obligation, status codes, why a reply has to reach a busy requester, and checking every
send are in [common/protocol-replying.md](../common/protocol-replying.md). Addresses are `tN`
([addressing.md](addressing.md)). This file is how hc carries the reply.

## Send the reply with `hc send`, without cutting the requester's turn

**`hc send` the reply to the tag's `reply`**; no `esc`, no `hc interrupt`, and no `interrupted`
attribute. Measured with Claude Code: a message sent while it was `working` was queued and fed into
the running turn at the next tool-call boundary, so the requester sees it before concluding. Other
agents were not measured.

Build the body with a heredoc, and for long results write a file and send its path.

```bash
body=$(cat <<'EOF'
<herdr res="<id from the tag received>" from="<my tN>" to="<reply value>" status="ok" fanout="<echo the value received>">
Two places. A missing expiry check in the auth middleware, and the exit condition of the retry loop.
</herdr>
EOF
)
hc send <reply value> "$body"
```

Check the exact arguments with `hc send --help`.

## Check every reply send

A refusal means **the reply did not go through.**

- **`blocked`**: the requester is waiting on a person. hc refuses the send unless forced; never force
  it. Tell the user, and send after that answer is handled.
- **`finished`**: the requester is gone. Tell the user where the result is.
