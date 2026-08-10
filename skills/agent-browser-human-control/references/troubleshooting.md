# Troubleshooting

## Symptoms

| Symptom | Cause and fix |
|---|---|
| Hangul does not appear | Nothing is focused. Click the field with `humanClick` first. |
| A keydown handler never sees Hangul | Expected: composition uses `keyCode: 229`. The page must listen on `composition*` events. |
| Every action looks like a different person | No persona was injected. Share one instance across all modules. |
| Typing is too fast or too slow | Adjust the persona's `strokesPerMin` — see `persona.md`. |
| Clicks are not centered | Intended gaussian spread. Pass coordinates from `getElementCenter` for dead center. |
| Drag does nothing | The page uses the HTML5 drag API. `humanDrag` emits mouse events only. |
| The wheel does not scroll | The scroll container is not under the cursor: `humanWheel(send, dy, { target: "#scrollable" })`. |
| Element not found in an SPA | Selector calls wait ~5 s. Extend it: `getElementBox(send, sel, { timeoutMs: 15000 })`. |
| `navigator.webdriver` is still true | `applyStealth` must run before `page.goto`; it only affects documents loaded afterward. |
| A tap is ignored on a mobile page | `enableTouch(send)` was not called, so the page does not consider the context touch-capable. |

## Emitted event sequences

Useful for verifying that input arrives as intended, and for writing assertions against
it.

| Action | Sequence |
|---|---|
| ASCII `'a'` | `keydown(KeyA, kc=65)` → `keypress` → `input` → `keyup` |
| Fast rollover `'as'` | `keydown(a)` → `keydown(s)` → `keyup(a)` → `keyup(s)` (overlapping) |
| Hangul `'안'` (3 strokes) | `keydown(KeyD, kc=229)` → `compositionstart` → `compositionupdate "ㅇ"` → `keyup(KeyD, kc=68)` → twice more → `compositionend "안"` + `input` |
| Click | `mouseMoved × N` (integer coordinates, plus a correction leg when overshooting) → `mousedown` → press drift → `mouseup` → `click` |
| Wheel | `wheel × ticks`, typically 4–26, spaced log-normally |
| Drag | `mousedown` → `mouseMoved × N` with `button: left` → `mouseup` |
| Tap | `touchStart` with one point → optional `touchMove` drift → `touchEnd` with an empty array |
| Swipe | `touchStart` → `touchMove × N` along a curve → `touchEnd` with an empty array |

## Verifying which events a node wants

When it is unclear whether an element expects mouse or touch input, ask the page
directly through CDP:

```js
const { result } = await send("Runtime.evaluate", {
  expression: "document.querySelector('#target')",
  objectGroup: "probe",
});
const listeners = await send("DOMDebugger.getEventListeners", { objectId: result.objectId });
```

The returned list names each event type the node is listening for, which settles whether
to reach for `human-mouse` or `human-touch`.
