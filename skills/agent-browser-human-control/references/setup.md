# Setup

Getting from "a browser exists" to "the modules can drive it" takes three pieces: a
`send` adapter, a persona, and optionally the stealth patch.

## 1. The `send` adapter

Every action function takes `send` first, shaped `(method, params) => Promise`. Supply
one of these.

### Playwright

```js
const cdp  = await page.context().newCDPSession(page);
const send = (m, p) => cdp.send(m, p);
```

### Puppeteer

```js
const cdp  = await page.target().createCDPSession();
const send = (m, p) => cdp.send(m, p);
```

### Raw CDP over WebSocket

For a Chrome that is already running with remote debugging enabled, first find the
target:

```js
import http from "node:http";

function getJson(path, port = 9222) {
  return new Promise((resolve, reject) => {
    http.get({ host: "127.0.0.1", port, path }, (res) => {
      let d = "";
      res.on("data", (c) => (d += c));
      res.on("end", () => resolve(JSON.parse(d)));
    }).on("error", reject);
  });
}

const targets = await getJson("/json/list");
const target  = targets.find((t) => t.type === "page" && /example\.com/.test(t.url));
```

Then open a socket and adapt it. CDP replies carry the `id` of the request, so pending
promises are resolved by matching that id:

```js
function connect(wsUrl) {
  const ws = new WebSocket(wsUrl);
  const pending = new Map();
  let id = 0;

  ws.onmessage = (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.id && pending.has(msg.id)) {
      const p = pending.get(msg.id);
      pending.delete(msg.id);
      msg.error ? p.reject(new Error(JSON.stringify(msg.error))) : p.resolve(msg.result);
    }
  };

  const open = new Promise((resolve, reject) => { ws.onopen = resolve; ws.onerror = reject; });

  return {
    send: async (method, params = {}) => {
      await open;
      const mid = ++id;
      ws.send(JSON.stringify({ id: mid, method, params }));
      return new Promise((resolve, reject) => pending.set(mid, { resolve, reject }));
    },
    close: () => ws.close(),
  };
}

const { send, close } = connect(target.webSocketDebuggerUrl);
await send("Runtime.enable");
await send("Page.enable");
await send("Page.bringToFront");   // input goes to the focused tab
```

`Page.bringToFront` matters when several tabs are open — input events land on whichever
tab is frontmost, not on the one whose socket you hold.

## 2. The persona

Create it once and hand the same instance to every module. Two modules with two
personas produce one session that behaves like two different people.

```js
import { createPersona } from "{SKILL_DIR}/scripts/persona.mjs";
import * as mouse from "{SKILL_DIR}/scripts/human-mouse.mjs";
import * as kbd   from "{SKILL_DIR}/scripts/human-keyboard.mjs";
import * as touch from "{SKILL_DIR}/scripts/human-touch.mjs";

const persona = createPersona("session-1");   // seeded, so the run is reproducible
mouse.setPersona(persona);
kbd.setPersona(persona);
touch.setPersona(persona);
```

Traits and how to adjust them: `persona.md`.

## 3. Stealth (optional)

Realistic input does not help if the browser announces itself as automated, so this
module overwrites the signals most commonly checked — `navigator.webdriver`,
`window.chrome`, `languages`, `plugins`, `permissions.query`, WebGL vendor/renderer, and
leftover automation globals.

```js
import { applyStealth, applyStealthCDP, STEALTH_LAUNCH_ARGS } from "{SKILL_DIR}/scripts/stealth.mjs";

// Playwright / Puppeteer — before page.goto
const browser = await chromium.launch({ args: STEALTH_LAUNCH_ARGS });
const ctx = await browser.newContext();
await applyStealth(ctx);          // accepts a page or a context

// Raw CDP equivalent
await applyStealthCDP(send);
```

Both inject on every new document, which means they take effect from the *next*
navigation onward and cannot retrofit a page that has already loaded. Call them before
`goto`.

This covers first-order signals only. Detection that combines many signals still sees
through it, so pair it with `playwright-extra` and its stealth plugin when that matters.

## Order of operations

```
launch with STEALTH_LAUNCH_ARGS
  → applyStealth(context)
    → enableTouch(send)          (only if using touch)
      → page.goto(...)
        → createPersona + setPersona on each module
          → input
```

Stealth and touch capability both need to be in place before the page loads, because a
page that feature-detects at load time reads them once and caches the result.
