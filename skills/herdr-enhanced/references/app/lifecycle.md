# Lifetimes and cleanup in hc mode

The principles — close only what you created, do not resurrect what is gone, the working directory is
fixed at start — are in [common/lifecycle.md](../common/lifecycle.md). This file is how hc terminal
lifetimes work and how to clean up.

## Who outlives whom

- **A terminal you start with `hc run` is your child.** It ends when your program ends (measured).
- **Add `--outlive-parent` when it should stay after you end** — a peer meant to keep its context.
  With it, the child still sends notes to the parent while the parent lives, and keeps the ended
  parent's address afterwards; sends to that address are refused as `finished` (measured).
- **`scripts/app/hc-layout open` starts terminals with `--no-parent --keep`**, like the app's own:
  they outlive the agent that asked ([layout.md](layout.md)).

## Clean up only what you started

- On terminals you launched: `hc kill`, then `hc rm`. Name each address exactly; never clear by name
  pattern.
- `hc-layout` removes its own placeholders (`sh -c 'while :; do sleep 3600; done'`, which `place`,
  `open` to the left or up, and `move-tab` split on the app route). When the command ends, whether it
  succeeded or failed, each one it made is closed, `hc kill`ed and `hc rm`ed by its own address; one
  already gone counts as removed. It never closes a pane it did not create. If one cannot be removed,
  the error names its address: `hc kill` and `hc rm` that address only. Measured: `pane.close` ends the placeholder, `hc kill` also takes its pane
  away, and `hc kill` on a finished terminal is a no-op.
- A terminal that is gone is gone: treat the goal as met, as
  [common/lifecycle.md](../common/lifecycle.md) says.
