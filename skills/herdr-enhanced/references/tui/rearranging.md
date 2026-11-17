# Rearranging panes inside one tab with the herdr CLI

Why a wrong layout has to be fixed before a person sees it, and why focus must not move, are in
[common/layout-direction.md](../common/layout-direction.md) and
[common/layout-arranging.md](../common/layout-arranging.md). This file is which herdr operation
actually rearranges a tab, and what each one keeps and changes.

## `pane move` into the pane's own tab does nothing

**`pane move` into the pane's own tab is a no-op that reports success** (measured). With or without
`--target-pane`, it exits 0 and the layout stays exactly as it was. The only trace is in the
response:

```
"move_result": {"changed": false, "reason": "same_tab", ...}
```

So never use it for same-tab moves, and **read `changed` in every `pane move` and `pane swap`
response** — a `false` there is the whole error report. This is the trap that sent several sessions
off moving panes through a temporary tab by improvisation.

## Swap, or move out and back

Two operations do rearrange a tab, and they keep and change different things (all measured).

| | `pane swap` | Move out to a temporary tab, then back |
|---|---|---|
| What changes | Only **which pane sits in which slot.** The split tree (directions, ratios) stays as it was | The **shape.** The pane leaves its slot (its sibling takes the space) and comes back as a new split next to `--target-pane` |
| Pane IDs, agent names | Kept | Kept — the pane stays in the same workspace, so its ID does not change |
| Focus | **Moves to the source pane**, and herdr **switches the screen to that tab and workspace** even if the person was looking elsewhere. There is no `--no-focus` | Unchanged with `--no-focus` — **unless the moved pane was the focused one in its tab:** focus then passes to another pane and does not come back |
| Leftovers | None | The temporary tab **closes itself** once its only pane leaves |

`pane swap --direction` with no pane on that side also exits 0 with `"changed": false` and
`"reason": "no_neighbor"`.

Choose by what the result should look like.

1. **Two panes trade places and the shape stays** → `pane swap --source-pane --target-pane`. Make
   the source **the pane that has focus in that tab**, if it is one of the two; then focus stays on
   the same pane. Swap only in the tab the person is looking at, since a swap elsewhere pulls their
   screen there — for a tab out of view, use the two-step move even for a plain exchange.
2. **The shape changes** (a column becomes a stack, a pane joins another column, a split flips
   direction) → the two-step move below. Swap cannot change shape, and the same-tab move does
   nothing.

## The two-step move

The two-step move is the documented procedure, not a workaround. Run it with `--no-focus` on both
steps, check `changed` on each, and confirm the temporary tab is gone.

```bash
pane_to_move=<pane id>      # the pane to move
anchor_pane=<pane id>       # the pane in the same tab it should sit beside
side=down                   # where it goes relative to the anchor: right or down

pane_info=$(herdr pane get "$pane_to_move" \
  | python3 -c 'import sys, json; p = json.load(sys.stdin)["result"]["pane"]; print(p["tab_id"], p["workspace_id"])')
home_tab=${pane_info% *}
home_workspace=${pane_info#* }
[ -n "$home_tab" ] || { echo "could not read the pane; nothing moved" >&2; exit 1; }

# 1) Out to a temporary tab that holds only this pane.
temp_tab=$(herdr pane move "$pane_to_move" --new-tab --workspace "$home_workspace" --label tmp-move --no-focus \
  | python3 -c 'import sys, json; m = json.load(sys.stdin)["result"]["move_result"]; print(m["pane"]["tab_id"] if m["changed"] else "")')
[ -n "$temp_tab" ] || { echo "step 1 did not move the pane; nothing changed" >&2; exit 1; }

# 2) Back into the original tab, beside the anchor.
landed_tab=$(herdr pane move "$pane_to_move" --tab "$home_tab" --split "$side" --target-pane "$anchor_pane" --no-focus \
  | python3 -c 'import sys, json; m = json.load(sys.stdin)["result"]["move_result"]; print(m["pane"]["tab_id"] if m["changed"] else "")')
[ "$landed_tab" = "$home_tab" ] \
  || { echo "step 2 failed: the pane is still in $temp_tab — bring it back before anything else" >&2; exit 1; }

# 3) The temporary tab should have closed itself. Confirm it is gone.
herdr tab get "$temp_tab" >/dev/null 2>&1 && echo "temporary tab $temp_tab is still open — close it" >&2
```

**A temporary tab must not outlive the procedure.** If step 2 fails, the pane is stranded in a tab
the person never asked for; move it back (or report where it is) before doing anything else. Use
`--new-tab` rather than `tab create` for step 1 — a tab from `tab create` comes with its own shell
pane, so it stays open after the move and you would have to close it yourself.

Then verify with `pane layout` as in [splitting.md](splitting.md). `--ratio` on step 2 is the share
the anchor keeps, the same as in a split (measured: `--ratio 0.25` beside a 120-column anchor left it
30 wide).
