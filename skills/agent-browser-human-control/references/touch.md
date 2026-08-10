# Touch

`{SKILL_DIR}/scripts/human-touch.mjs`

Some mobile pages attach listeners only to `touchstart`/`touchend` — keypads, carousels,
certain buttons. Mouse events never reach those, however precise the coordinates.
This module fills that path with `Input.dispatchTouchEvent`.

**Two layers are needed.** First make the context touch-capable with `enableTouch(send)`,
which exposes `navigator.maxTouchPoints > 0` and `'ontouchstart' in window === true`.
Then fire the actual sequence. A page that feature-detects touch support will hide its
touch UI, or ignore the input, when the first layer is missing. Under Playwright,
`newContext({ hasTouch: true, isMobile: true })` before `goto` is more robust still,
because the page reads those properties as it loads.

## Functions

| Function | Returns | Purpose |
|---|---|---|
| `enableTouch(send, opts?)` | `void` | Make the context touch-capable; `{maxTouchPoints=1, emitForMouse=false}` |
| `disableTouch(send)` | `void` | Revert it |
| `humanTap(send, target, opts?)` | `{x,y}` | Tap: touchStart → hold → touchEnd |
| `humanLongPress(send, target, opts?)` | `{x,y}` | Hold, 600 ms by default |
| `humanSwipe(send, from, to, opts?)` | `{x,y}` | Press, curve to the target, release |
| `humanTouchScroll(send, deltaY, opts?)` | `void` | Flick-based scroll; positive scrolls down |
| `getLastTouch()` / `isTouchEnabled()` | | Last tap coordinates / whether touch is on |
| `setPersona(p)` / `getPersona()` | | Persona injection and lookup |

## Options

**`humanTap`**

- `holdMs` — contact duration in ms (default: persona-derived, around 60 ms)
- `spread` — shrink factor for the landing spread on selector or bbox targets
  (default 0.5). Use `0` for small keys.
- `drift` — micro-movement during contact, on or off (default: probabilistic)
- An explicit `{x,y}` lands exactly there with no spread, which is what precision
  targets want. Selector and bbox targets spread inside the element, though less
  than a mouse click does.

**`humanSwipe`** — `duration` (default proportional to distance), `steps` (number of
touchMove events), `curviness`

**`humanTouchScroll`** — `target` (where the scroll originates), `span` (distance per
flick, default 480), `duration`

## Choosing a call

| Goal | Call |
|---|---|
| Enable touch first | `await enableTouch(send)` — once, before `goto` and input |
| Tap a mobile button | `humanTap(send, "#btn")` |
| Hit a key that only listens on `touchstart` | `humanTap(send, { x, y })` — exact, no spread |
| Long-press for a context menu | `humanLongPress(send, "#item")` |
| Advance a carousel | `humanSwipe(send, "#slide", { x: 40, y: 400 })` |
| Scroll the page by touch | `humanTouchScroll(send, 600)` |

## Notes

- **Touch capability comes first.** Calling `humanTap` without `enableTouch` may be
  silently ignored by a page that checks `maxTouchPoints` or `ontouchstart`.
- **CDP contract.** `touchStart` and `touchMove` carry at least one point;
  `touchEnd` and `touchCancel` carry an empty array. The module handles this.
- **Do not mix input types on one element.** If a node listens for mouse events use
  `human-mouse`; if it listens for touch use `human-touch`. To find out which,
  inspect it with CDP `DOMDebugger.getEventListeners`.
