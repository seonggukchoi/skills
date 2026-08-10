---
name: agent-browser-human-control
description: >-
  Human-like browser input over Chrome DevTools Protocol — curved mouse movement with
  overshoot correction, gaussian click spread, hover, wheel, drag, typing with realistic
  rhythm and typos, Hangul IME composition, touch tap/swipe, and a consistent
  per-session persona. Use this whenever input should look hand-driven rather than
  scripted: pages that ignore or reject synthetic events, driving an already-open Chrome
  tab over remote debugging, mobile elements that only listen on touchstart/touchend,
  reproducible typing speed for demos and recordings, or when plain Playwright/Puppeteer
  click() and fill() are too instantaneous to be representative. Works with
  agent-browser, Playwright, Puppeteer, and chrome-remote-interface alike.
---

# Browser Human Control

Drives a page through CDP `Input.*` events shaped to look hand-driven: curved mouse
paths with overshoot correction, gaussian click spread, log-normal typing intervals,
IME composition for Hangul, and touch gestures.

Six ES modules live in `scripts/`. They have no runtime dependencies and import each
other by relative path, so they run as-is from wherever this skill is installed.

`{SKILL_DIR}` below means the directory holding this SKILL.md — resolve it to an
absolute path when writing import statements.

## Modules

| Module | Covers | Reference |
|---|---|---|
| `human-mouse.mjs` | move, click, hover, wheel, drag, idle jitter | `references/mouse.md` |
| `human-keyboard.mjs` | typing, special keys, Hangul IME, typos | `references/keyboard.md` |
| `human-touch.mjs` | tap, long-press, swipe, touch scroll | `references/touch.md` |
| `persona.mjs` | per-session traits: speed, curvature, typo rate | `references/persona.md` |
| `stealth.mjs` | hides first-order automation signals | `references/setup.md` |
| `human-random.mjs` | seeded RNG and distributions used by the modules above | — |

## Conventions

Four rules hold everywhere, and getting them wrong accounts for most failures:

- **Every action takes `send` as its first argument** — an adapter shaped
  `(method, params) => Promise`. This is what keeps the modules driver-agnostic:
  anything that can speak CDP can supply one.
- **Targets are a CSS selector or `{x, y}`.** Selector-based calls wait for the element
  (~5s) and scroll it into view with a wheel gesture when it is offscreen, so an
  element below the fold needs no special handling.
- **Coordinates are CSS pixels**, viewport-relative.
- **Inject one persona into every module you use.** Skipping this does not raise an
  error — each module lazily builds its own random persona instead, so the mouse and
  the keyboard end up behaving like two different people in one session.

## Quick start

```js
import * as mouse from "{SKILL_DIR}/scripts/human-mouse.mjs";
import * as kbd   from "{SKILL_DIR}/scripts/human-keyboard.mjs";
import { createPersona } from "{SKILL_DIR}/scripts/persona.mjs";

// One session = one person. Seed it to reproduce the same behavior later,
// or omit the seed for a different person each run.
const persona = createPersona("session-1");
mouse.setPersona(persona);
kbd.setPersona(persona);

const cdp  = await page.context().newCDPSession(page);   // Playwright
const send = (m, p) => cdp.send(m, p);

await mouse.humanClick(send, "input[name='q']");
await kbd.humanType(send, "hello");
await mouse.humanClick(send, "button[type='submit']");
```

Typing speed, curvature, and typo rate all come from the persona rather than from call
options, which is why the calls above carry no tuning arguments.

## Where to go next

Read only the file you need — each is self-contained.

| Need | Read |
|---|---|
| Wire up Playwright, Puppeteer, or a raw CDP socket; attach to an open tab | `references/setup.md` |
| Move, click, hover, scroll, or drag | `references/mouse.md` |
| Type text, press special keys, control typos | `references/keyboard.md` |
| Tap, swipe, or reach elements that only listen on touch events | `references/touch.md` |
| Change typing speed or any other trait | `references/persona.md` |
| Input does nothing, or behaves unlike a person | `references/troubleshooting.md` |
