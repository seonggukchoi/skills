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
- `hc-layout` removes its own placeholders (`sh -c 'while :; do sleep 3600; done'`); it never closes
  a pane it did not create.
- A terminal that is gone is gone: treat the goal as met, as
  [common/lifecycle.md](../common/lifecycle.md) says.
