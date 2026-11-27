# app: doing it in the herdr app with hc

For the herdr app, built on herdr-core, where agents talk through the `hc` CLI. You are in hc mode
when `$HC_TERMINAL_ID` is set; that value is your own address. `hc --skill` prints hc's own manual
and `hc <command> --help` gives exact arguments; the official `herdr` skill does not apply here.
The full map is [../INDEX.md](../INDEX.md).

**The judgment and the delegation contract do not change in hc mode** (the
[common/](../common/INDEX.md) documents); only the address values (`tN`) and the commands that carry
the text differ. Each document here opens with the `common/` documents it carries out — read those
for the reasons. Measured behavior was observed with Claude Code agents; anything not measured is marked as such.

| When you are | Read |
|---|---|
| Writing or reading a tag's addresses, a first request without `to`, or text wrapped in `<hc from>` | [addressing.md](addressing.md): `tN` not names, `to` on the first request, wrapping versus `reply` |
| Handing work to another terminal, starting a peer, or waiting for replies | [delegating.md](delegating.md): what hc already does, the carrier table, `hc wait --children`, dialogs |
| Replying to a `herdr` tag | [replying.md](replying.md): `hc send` without interrupting, `blocked` and `finished` refusals |
| Keeping a peer alive, or cleaning up terminals | [lifecycle.md](lifecycle.md): parent and child, `--outlive-parent`, `hc kill`/`hc rm` |
| Splitting, opening a tab, bringing a background terminal into a tab, setting ratios, or moving a tab, on any machine | [layout.md](layout.md): `scripts/app/hc-layout` commands, `verified`, limits |
| The script reports `"via": "doc"`, refuses an unknown document shape, or you consider `--via` | [layout-routes.md](layout-routes.md): app route versus doc route, writing the document only through the script |
