# herdr-enhanced references

The references are split by what they answer, so you read only what the situation needs.

| Directory | What it answers | Index |
|---|---|---|
| `common/` | **What to decide and why**, in either mode: targets, layout judgment, lifetimes, reading screens, diagnosing, delegation, and the request/reply contract | [common/INDEX.md](common/INDEX.md) |
| `tui/` | **How to do it with the herdr TUI's `herdr` CLI** (`HERDR_ENV=1` or `$HERDR_PANE_ID` set) | [tui/INDEX.md](tui/INDEX.md) |
| `app/` | **How to do it in the herdr app with `hc` and `scripts/app/hc-layout`** (`$HC_TERMINAL_ID` set) | [app/INDEX.md](app/INDEX.md) |

How to read them:

1. Find the situation in your mode's index (`tui/` or `app/`).
2. Each document there opens with links to the `common/` documents it carries out. **Read the
   `common/` document for the judgment, then the mode document for the commands.** A mode document
   does not repeat the reasons.
3. The `common/` documents link back to both modes, so you can also start from a principle.

Command syntax itself is not here: the official `herdr` skill and `herdr --help` hold the TUI's, and
`hc --skill` and `hc <command> --help` hold hc's.

## Every document

**common/**, judgment for both modes, indexed by situation in [common/INDEX.md](common/INDEX.md):

- [environment.md](common/environment.md): telling the herdr TUI, the herdr app, and neither apart on positive evidence; why terminal-app variables mislead; never driving the terminal emulator.
- [targeting.md](common/targeting.md): "here" is the pane the instruction arrived in; never omit the target; stop instead of falling back; names to people, addresses to commands; panes stay in the tab they were made in.
- [layout-direction.md](common/layout-direction.md): translating the person's words into a split direction; "horizontal"/"vertical" are ambiguous; an instruction beats the shape rule; verifying the result.
- [layout-arranging.md](common/layout-arranging.md): several panes with even shares; not stacking one way; resizing and zoom; offering candidates; keeping focus; reporting layouts that cannot be built.
- [lifecycle.md](common/lifecycle.md): the working directory is fixed at start; close only what you created; do not resurrect what is gone; a revived session does not know; status names are observations.
- [reading-screens.md](common/reading-screens.md): suggestion text is not the user's words; a question on screen is not an answer; dialogs are questions to a person.
- [diagnosing.md](common/diagnosing.md): an unexplained failure means a wrong premise; circumstance is not cause; no resend on a failed confirmation; no transcript parsing.
- [delegation.md](common/delegation.md): what makes it a delegation; whether to delegate; panes versus subagents; picking targets by status; wording the request; splitting work; silent omissions.
- [protocol-tag.md](common/protocol-tag.md): the request/reply tag, its attributes, addresses, and why the tag alone loads this skill on the other side.
- [protocol-replying.md](common/protocol-replying.md): the reply obligation and status codes; replying to `reply`; reaching a busy requester; checking every send; sent versus received.
- [protocol-waiting.md](common/protocol-waiting.md): ending your turn after delegating; holding synthesis until `fanout` replies are in.
- [protocol-chains.md](common/protocol-chains.md): supporting queries versus handover; keeping the original `id`; `hop` limits; the collaboration record.

**tui/**, doing it with the `herdr` CLI, indexed by situation in [tui/INDEX.md](tui/INDEX.md):

- [targeting.md](tui/targeting.md): `--current` and `$HERDR_PANE_ID` per command; IDs and names; renaming; checking membership and pulling a drifted pane back.
- [splitting.md](tui/splitting.md): `--direction right|down`; split-then-swap for left and top; reading coordinates with `pane layout`; verification commands that read backwards.
- [rearranging.md](tui/rearranging.md): the same-tab `pane move` no-op; `pane swap` versus the two-step move; the two-step procedure.
- [sizing.md](tui/sizing.md): `--ratio` arithmetic for equal panes; `resize` direction meaning; zoom; notifications; what the TUI cannot express.
- [lifecycle.md](tui/lifecycle.md): `--cwd`; ending only the agent with its exit command; listing without narrowing scope.
- [delegating.md](tui/delegating.md): building the roster; why `agent start` arguments cannot carry work; starting a peer in three steps; no `--wait`.
- [replying.md](tui/replying.md): the reply block (status, `esc`, `agent_blocked`); what herdr cannot tell; rerunning after a reply cut your turn.
- [diagnosing.md](tui/diagnosing.md): reading state instead of screen text; symptoms and the premise to doubt; the source of truth for live targets.

**app/**, doing it with `hc` and `scripts/app/hc-layout`, indexed by situation in [app/INDEX.md](app/INDEX.md):

- [addressing.md](app/addressing.md): `tN` addresses, never names; a first request without `to`; the `<hc>` wrapping versus the tag's `reply`.
- [delegating.md](app/delegating.md): what hc already does; the TUI-versus-hc carrier table; `hc wait --children`; dialogs.
- [replying.md](app/replying.md): `hc send` without interrupting; the `blocked` and `finished` refusals.
- [lifecycle.md](app/lifecycle.md): parent and child lifetimes, `--outlive-parent`, `hc kill`/`hc rm` on what you started.
- [layout.md](app/layout.md): `scripts/app/hc-layout` commands, `--ratio`, `verified`, and limits on either route.
- [layout-routes.md](app/layout-routes.md): the app route versus the doc route; writing the layout document only through the script.
