# Splitting a pane with the herdr CLI

Translating the person's words into a direction, never passing "horizontal" or "vertical" through,
and letting an instruction override the shape rule are in
[common/layout-direction.md](../common/layout-direction.md). This file is how to split and verify
with `herdr`.

## `--direction` takes only `right` and `down`

| Layout to build | `--direction` |
|---|---|
| side by side (left and right) | `right` |
| stacked (top and bottom) | `down` |

There is no `left`, `up`, `horizontal`, or `vertical`. A request to put something on the left or on
top cannot be passed through directly, so use the next section.

`pane neighbor`, `focus`, `resize`, and `swap` all take four directions. That makes direction
arguments look universal, but **only the splitting command is limited to two.**

## Left and top mean splitting first, then swapping

`pane split` creates a new pane **only to the right or below.** When a person says "open it on the
left", split right and then swap the two panes with `pane swap`.

```bash
NEW=$(herdr pane split --current --direction right --cwd "$PWD" --no-focus \
      | python3 -c 'import sys, json; print(json.load(sys.stdin)["result"]["pane"]["pane_id"])')
[ -n "$NEW" ] || { echo "split failed — not swapping" >&2; exit 1; }
herdr pane swap --source-pane "$HERDR_PANE_ID" --target-pane "$NEW"
```

**Do not drop the empty check.** herdr writes errors to stderr and exits 1, so a failed split leaves
`python3` with empty input and `NEW` silently an empty string. Pass that through as
`--target-pane ""` and **an empty target is not "no target" — it is read as "the current screen"**
([common/targeting.md](../common/targeting.md)), swapping places with the pane the person was
watching. This is where this document's own example would cause the incident it exists to prevent.

A request for the top works the same way — split `down`, then swap. **Swapping moves your own pane.**
The place the person was looking at changes, so say in your report that you swapped. Focus also goes
to the source pane — here your own — and herdr shows that tab (measured), so this pattern fits only
when your pane is the one on screen. The details are in [rearranging.md](rearranging.md).

## Verify the layout after splitting

**The `pane split` response carries no coordinates** (measured). What comes back is `pane_id`,
`cwd`, and `tab_id`, so that response alone cannot tell you whether the new pane appeared to the
right or below. So read the coordinates separately after splitting.

```bash
herdr pane layout --pane "$HERDR_PANE_ID" | python3 -c '
import sys, json
d = json.load(sys.stdin)["result"]["layout"]
for p in sorted(d["panes"], key=lambda q: (q["rect"]["y"], q["rect"]["x"])):
    r = p["rect"]
    print(p["pane_id"], "x=%d y=%d w=%d h=%d" % (r["x"], r["y"], r["width"], r["height"]))
'
```

The criterion is **the coordinate relationship between the reference pane and the new one.**

- **Placed left and right** — `x` differs, `y` matches. The new pane has the larger `x`.
- **Placed top and bottom** — `y` differs, `x` matches. The new pane has the larger `y`.

The same response's `splits` array carries each split's `direction` and `ratio` directly. With
several panes, that is the easier read.

If it came out wrong, **fix it before handing back to a person.** Close it and split again if it is
empty; otherwise rearrange it inside the tab as [rearranging.md](rearranging.md) describes.
`pane move --tab` aimed at the tab the pane is already in does nothing.

## Verification commands that read backwards

The very commands called to verify a layout invite a misreading. Read backwards, **they convince you
a wrong layout is right.**

| Command | Easy to read backwards as | What it actually means (measured) |
|---|---|---|
| `pane edges` | `right: true` meaning "there is a neighbor on the right" | **`true` means that side is an outer boundary.** With a neighbor it is `false` |
| `pane neighbor` | It succeeded, so there is a neighbor that way | It **succeeds with exit code 0 even with no neighbor.** The `neighbor_pane_id` key is simply absent |
| `pane split` response | The response is fine, so it split the way I asked | **The response carries no coordinates.** It cannot tell you whether the direction was right |
| `pane move` / `pane swap` response | Exit code 0, so it moved | **Both exit 0 when nothing changed.** A move into the pane's own tab returns `"changed": false, "reason": "same_tab"`; a swap with no neighbor returns `"reason": "no_neighbor"`. Read `changed` |

So verify layout with the coordinates from `pane layout`, as above.
