# common: judgment that holds in both modes

These documents say **what to decide and why**. They hold in the herdr TUI and in the herdr app
alike; each opens with links to the [tui/](../tui/INDEX.md) and [app/](../app/INDEX.md) documents
that carry it out. The full map is [../INDEX.md](../INDEX.md).

| When you are | Read |
|---|---|
| Unsure whether this is herdr, or which kind | [environment.md](environment.md): positive evidence, misleading terminal-app variables, never driving the terminal emulator |
| Choosing which pane a command acts on, or telling a person which pane you mean | [targeting.md](targeting.md): "here" is the instruction's pane, never omit the target, stop instead of falling back, names to people, panes stay in their tab |
| Splitting one pane | [layout-direction.md](layout-direction.md): translating the person's words, "horizontal"/"vertical", instruction over shape, verifying the result |
| Opening several, sizing, tidying, or facing an ambiguous layout request | [layout-arranging.md](layout-arranging.md): even shares, not stacking one way, resizing and zoom, offering candidates, focus, reporting what cannot be built |
| Starting something, closing something, or finding something gone | [lifecycle.md](lifecycle.md): working directory fixed at start, close only what you created, no resurrection, revived sessions, status names |
| Reading another pane's screen to decide | [reading-screens.md](reading-screens.md): suggestion text, questions left on screen, dialogs |
| Facing a failure or a result that looks wrong | [diagnosing.md](diagnosing.md): recheck premises, circumstance is not cause, no resend on failed confirmation, no transcript parsing |
| Deciding whether and to whom to hand work | [delegation.md](delegation.md): what counts as delegation, doing it yourself, panes versus subagents, status-based targets, wording, splitting, omissions |
| Sending a request, or you received a `herdr` tag | [protocol-tag.md](protocol-tag.md): the tag, attributes, addresses, the tag as the trigger |
| Replying | [protocol-replying.md](protocol-replying.md): obligation, status codes, reply to `reply`, busy requesters, checking sends |
| Waiting for replies, or one reply arrived | [protocol-waiting.md](protocol-waiting.md): end the turn, hold synthesis until `fanout` replies are in |
| Work you took on needs another pane | [protocol-chains.md](protocol-chains.md): supporting query versus handover, keep the `id`, `hop` limits |
