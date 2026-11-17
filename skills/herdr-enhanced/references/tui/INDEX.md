# tui: doing it with the herdr CLI

For the herdr TUI (`HERDR_ENV=1` or `$HERDR_PANE_ID` set). Command syntax is in the official `herdr`
skill and `herdr --help`; these documents hold the judgment-bearing details and measurements for
each operation. **Each one opens with the [common/](../common/INDEX.md) documents it carries out —
read those for the reasons.** The full map is [../INDEX.md](../INDEX.md).

| When you are | Read |
|---|---|
| Naming a target, using `--current` or `$HERDR_PANE_ID`, renaming, or checking a pane stayed in your tab | [targeting.md](targeting.md): per-command target slots, IDs versus names, membership checks |
| Splitting a pane, including to the left or top, and verifying it | [splitting.md](splitting.md): `--direction right\|down`, split-then-swap, `pane layout` coordinates, commands that read backwards |
| Moving or swapping panes inside one tab | [rearranging.md](rearranging.md): the same-tab `pane move` no-op, `pane swap` versus the two-step move, the procedure |
| Opening several equal panes, resizing, zooming, or alerting the person | [sizing.md](sizing.md): `--ratio` arithmetic, `resize` direction meaning, zoom, notifications, what the TUI cannot express |
| Choosing a working directory, ending an agent, or finding something gone | [lifecycle.md](lifecycle.md): `--cwd`, `/exit` through `agent prompt`, unscoped listings |
| Handing work to another pane or starting a new peer | [delegating.md](delegating.md): roster, startup arguments, the three-step start, no `--wait` |
| Replying to a `herdr` tag, or a reply cut your turn | [replying.md](replying.md): the reply block, its judgments, what herdr cannot tell, rerunning cut work |
| A command behaved unexpectedly, or reading another agent's state | [diagnosing.md](diagnosing.md): `agent get`/`agent read`, symptoms and premises, the source of truth |
