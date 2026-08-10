# Mouse

`{SKILL_DIR}/scripts/human-mouse.mjs`

Movement follows a bezier path with noise tapered at both ends and a variable speed
profile, plus overshoot submovements — the cursor slightly passes the target and
corrects back, the way a hand does. Coordinates are rounded to integers and unchanged
positions are skipped, because real hardware emits nothing while the mouse is still.

## Functions

| Function | Returns | Purpose |
|---|---|---|
| `humanMoveTo(send, target, opts?)` | `{x,y}` | Move, including overshoot correction |
| `humanClick(send, target, opts?)` | `{x,y}` | Move, then click with gaussian spread inside the element |
| `humanHover(send, target, opts?)` | `{x,y}` | Move, then dwell with micro-jitter |
| `humanWheel(send, deltaY, opts?)` | `void` | Wheel scroll, split into ticks that accelerate and decelerate |
| `humanDrag(send, from, to, opts?)` | `{x,y}` | Press, curve to the target, release |
| `startIdleJitter(send, opts?)` / `stopIdleJitter()` | `void` | Background micro-movement between actions |
| `getElementBox(send, selector, opts?)` | bbox | `{x,y,width,height,cx,cy,vw,vh,inView}`; waits and auto-scrolls by default |
| `getElementCenter(send, selector)` | `{x,y}` | Dead-center coordinates |
| `waitForSelector(send, selector, opts?)` | `true` | Poll until present; `{timeoutMs=5000, intervalMs=100}` |
| `getCursorPos()` / `setCursorPos(p)` | | Last known cursor position |
| `setPersona(p)` / `getPersona()` | | Persona injection and lookup |

## Options

Defaults come from the persona. Everything below is an override for one call.

**`humanMoveTo`** — inherited by click, hover, and drag

- `start: {x,y}` — starting point (default: last cursor position)
- `duration: number` — total travel time in ms (default: persona `moveDuration(dist)`)
- `jitter: number` — noise amplitude (default: persona `mouse.jitter`)
- `button: "none"|"left"|"right"|"middle"` — `"left"` while dragging
- `overshoot: boolean` — force on or off (default: distance > 140 px and persona probability)

**`humanClick`**

- `button: "left"|"right"|"middle"` (default `"left"`)
- `clickCount: number` — 2 for a double click
- The landing point is spread inside the element when the target is a selector or bbox.
  An explicit `{x,y}` is used verbatim.

**`humanHover`**

- `dwellMs: number` (default: persona `readPause`)
- `hoverJitter: number` — jitter radius in px (default: persona `idleRadius`)

**`humanWheel`**

- `deltaY: number` — positive scrolls down, negative up
- `deltaX: number` (default 0)
- `target: selector|{x,y}` — where the scroll originates (default: current cursor)
- `ticks: number` / `duration: number` (default: proportional to the distance)
- `pauseChance: number` — probability of a mid-scroll pause (default 0.12)

**`startIdleJitter`**

- `radius: number` (default: persona `idleRadius`)
- `intervalMin` / `intervalMax` in ms (default 600 / 2400)

## Choosing a function

| Goal | Call |
|---|---|
| Click a button or link | `humanClick(send, "#submit")` |
| Double click / right click | `humanClick(send, "...", { clickCount: 2 })` / `{ button: "right" }` |
| Trigger a tooltip | `humanHover(send, "...", { dwellMs: 1000 })` |
| Scroll down / up | `humanWheel(send, 600)` / `humanWheel(send, -300, { pauseChance: 0.35 })` |
| Drag an element | `humanDrag(send, "#card", "#zone-b")` |
| Keep the cursor alive between actions | `startIdleJitter(send)` … `stopIdleJitter()` |

## Notes

- **No HTML5 native drag.** `humanDrag` emits `mousedown → mousemove → mouseup`. Pages
  built on `dragstart`/`drop` need those events dispatched separately.
- **Clicks are intentionally off-center.** For dead center, pass coordinates from
  `getElementCenter` — explicit `{x,y}` skips the spread.
- **Idle jitter yields.** An internal busy counter suppresses jitter while another
  action is running, so the two never interleave.
- **Offscreen targets are handled.** Selector-based calls run `getElementBox`, which
  waits for the element and wheels it into view rather than teleporting the cursor. To
  opt out, take coordinates from `getElementBox(send, sel, { wait: false, scroll: false })`
  and pass them as `{x,y}`.
