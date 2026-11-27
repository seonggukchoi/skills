# How `hc-layout` reaches the layout: the app route and the doc route

Using the script is in [layout.md](layout.md). This file explains the two routes it chooses between,
and the rule for writing the layout document. Read it when the output says `"via": "doc"`, when the
script refuses with "a shape this script does not know", or before forcing a route with `--via`.

The code is under `scripts/app/hc_layout/`: `app.py` for the app route and the route choice, `doc.py`
and `edits.py` for reading and writing the layout document.

## Two routes, chosen automatically

| Route | When | How it changes the layout |
|---|---|---|
| `app` | `herdr-app status` works here (the computer with the Herdr window) | Public commands only. A placeholder pane is split where the terminal should go, the terminal joins the tab by labels and is swapped into the placeholder's slot, the placeholder closes. Every placeholder a command made is removed when it ends, even when it fails ([lifecycle.md](lifecycle.md)). `layout.resize` sets sizes. Nothing takes focus |
| `doc` | No Herdr app here (a remote machine over ssh) | Writes that machine's layout document with `doc.set`: the shape is checked first (unknown shape: nothing is written), the write carries the version read (another client wrote first: read again and retry), and the edit follows what the app itself writes. Then `herdr.space`/`herdr.tab` labels are set, since the app does not relabel |

Every client (desktop, mobile, another computer) draws from the machine's layout document, so both
routes show the same everywhere. Measured with herdr-app 0.1.16 and hc 0.1.21: the app picked up
`doc` writes at once, kept them alongside its own commands, and refused a stale version with
`conflict`. Not measured: a write while no app is running (the app reads the document when it
starts), and the mobile app's screen.

## Write the document only through the script's `doc` route

**Write the document only through the script's `doc` route**, and only where no app is reachable:
never with your own `doc.set`, and never with `--via doc` where `herdr-app status` works. Reading it
(`tree`, `where`) is fine anywhere.

If a newer Herdr stores the document differently, the script stops with "a shape this script does
not know" and changes nothing. Report that; do not work around it.
