// human-mouse.mjs (v2)
// CDP로 사람처럼 마우스를 움직이고 클릭/호버/스크롤/드래그한다.
//
// v2 개선점:
//   - 페르소나 연동: 세션 = 한 사람. 속도/곡선/정밀도 성향이 일관됨
//   - submovement: 목표를 살짝 지나쳤다(overshoot) 1~2회 보정해 도달 (Fitts' law)
//   - 정수 좌표 + 중복 스킵: 실제 하드웨어 마우스처럼 정수 픽셀, 안 움직이면 이벤트 없음
//   - 불규칙 이벤트 간격: 고정 fps가 아니라 폴링레이트+OS지연 흉내(로그정규 dt)
//   - 클릭 위치 가우시안 분산: 항상 정중앙이 아니라 요소 안에서 흩어짐
//   - press 드리프트: 누르는 동안 1~2px 미세 이동 후 release
//
// 좌표계는 CSS 픽셀. send = (method, params) => Promise.

import { createPersona } from "./persona.mjs";
import { clamp } from "./human-random.mjs";

// ============================================================
// 유틸
// ============================================================

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function cubic(p0, p1, p2, p3, t) {
  const u = 1 - t;
  return u*u*u*p0 + 3*u*u*t*p1 + 3*u*t*t*p2 + t*t*t*p3;
}
function smoothstep(t) { return t * t * (3 - 2 * t); }

// ============================================================
// 모듈 상태
// ============================================================

let cursorPos      = { x: 100, y: 100 };
let activePersona  = null;
let busyCount      = 0;
let idleConfig     = null;
let idleTimer      = null;
let lastEmitted    = { x: null, y: null };

export function setPersona(persona) { activePersona = persona; }
export function getPersona() {
  if (!activePersona) activePersona = createPersona();
  return activePersona;
}
export function getCursorPos() { return { ...cursorPos }; }
export function setCursorPos(p) { cursorPos = { x: p.x, y: p.y }; }

async function withBusy(fn) {
  busyCount++;
  try { return await fn(); }
  finally { busyCount--; }
}

// 정수 좌표로 이벤트 발송. 직전과 같은 정수면 스킵(실제 마우스는 안 움직이면 이벤트 없음).
async function emitMove(send, x, y, button = "none") {
  const ix = Math.round(x);
  const iy = Math.round(y);
  if (ix === lastEmitted.x && iy === lastEmitted.y) return false;
  await send("Input.dispatchMouseEvent", {
    type: "mouseMoved",
    x: ix, y: iy,
    button,
    pointerType: "mouse",
  });
  lastEmitted = { x: ix, y: iy };
  cursorPos = { x: ix, y: iy };
  return true;
}

// ============================================================
// selector → 좌표 / bbox
// ============================================================

/**
 * 요소가 나타날 때까지 폴링한다. timeoutMs 안에 못 찾으면 throw.
 * SPA에서 아직 렌더되지 않은 요소를 기다릴 때.
 */
export async function waitForSelector(send, selector, opts = {}) {
  const timeoutMs  = opts.timeoutMs  ?? 5000;
  const intervalMs = opts.intervalMs ?? 100;
  const deadline = Date.now() + timeoutMs;
  for (;;) {
    const { result } = await send("Runtime.evaluate", {
      expression: `!!document.querySelector(${JSON.stringify(selector)})`,
      returnByValue: true,
    });
    if (result.value) return true;
    if (Date.now() >= deadline) throw new Error(`waitForSelector timeout(${timeoutMs}ms): ${selector}`);
    await sleep(intervalMs);
  }
}

/**
 * selector → bbox. 기본으로 요소 등장을 대기(wait)하고, 뷰포트 밖이면
 * 사람처럼 휠로 스크롤해 들여놓은 뒤(scroll) 좌표를 다시 측정한다.
 * @param {object} [opts]
 * @param {boolean} [opts.wait=true]      요소 등장까지 폴링
 * @param {boolean} [opts.scroll=true]    뷰포트 밖이면 humanWheel로 들여놓기
 * @param {number}  [opts.timeoutMs=5000] wait 타임아웃
 */
export async function getElementBox(send, selector, opts = {}) {
  const wait   = opts.wait   ?? true;
  const scroll = opts.scroll ?? true;
  if (wait) await waitForSelector(send, selector, opts);

  const measure = async () => {
    const { result } = await send("Runtime.evaluate", {
      expression: `(() => {
        const el = document.querySelector(${JSON.stringify(selector)});
        if (!el) throw new Error("element not found: " + ${JSON.stringify(selector)});
        const r = el.getBoundingClientRect();
        return { x: r.left, y: r.top, width: r.width, height: r.height,
                 cx: r.left + r.width/2, cy: r.top + r.height/2,
                 vw: window.innerWidth, vh: window.innerHeight,
                 inView: r.top >= 0 && r.left >= 0 &&
                         r.bottom <= window.innerHeight && r.right <= window.innerWidth };
      })()`,
      returnByValue: true,
    });
    return result.value;
  };

  let box = await measure();
  if (scroll && !box.inView) {
    // 요소 중앙을 뷰포트 중앙 근처로 — 순간이동(scrollIntoView) 대신 사람처럼 휠 스크롤
    const deltaY = Math.round(box.cy - box.vh / 2);
    if (Math.abs(deltaY) > 4) {
      await humanWheel(send, deltaY);
      box = await measure(); // 스크롤 후 좌표 재측정
    }
  }
  return box;
}

export async function getElementCenter(send, selector) {
  const b = await getElementBox(send, selector);
  return { x: b.cx, y: b.cy };
}

// target: selector(string) | {x,y} | bbox객체 → 중앙 좌표
async function resolveCenter(send, target) {
  if (typeof target === "string") return await getElementCenter(send, target);
  if (target && typeof target.cx === "number") return { x: target.cx, y: target.cy };
  return { x: target.x, y: target.y };
}

// 클릭용: 요소 안에서 가우시안으로 흩어진 한 점 (정중앙 회피)
async function resolveClickPoint(send, target) {
  const p = getPersona();
  let box = null;
  if (typeof target === "string") box = await getElementBox(send, target);
  else if (target && typeof target.width === "number") box = target;

  if (!box) return await resolveCenter(send, target); // 좌표 직접 지정이면 그대로

  // 중앙 기준, 요소 크기의 clickPrecision 비율을 표준편차로. 가장자리 넘지 않게 절단.
  const sdX = (box.width  / 2) * p.mouse.clickPrecision;
  const sdY = (box.height / 2) * p.mouse.clickPrecision;
  const off = p.rng.gaussian2D(sdX, sdY);
  return {
    x: clamp(box.cx + off.x, box.x + 2, box.x + box.width  - 2),
    y: clamp(box.cy + off.y, box.y + 2, box.y + box.height - 2),
  };
}

// ============================================================
// 단일 곡선(leg) 이동
// ============================================================

// start → end 를 베지어 + taper 노이즈로 이동. 시간 기반 + 불규칙 dt.
async function moveLeg(send, start, end, duration, button, opts = {}) {
  const p = getPersona();
  const dx = end.x - start.x;
  const dy = end.y - start.y;
  const dist = Math.hypot(dx, dy);
  if (dist < 0.5) { await emitMove(send, end.x, end.y, button); return; }

  const curvy = p.mouse.curviness * (opts.curveScale ?? 1);
  const sign  = p.rng.bool() ? -1 : 1;
  // 곡률 진폭은 거리에 비례해 상한을 둔다 — 짧은 이동에서 과도하게 휘지 않게.
  const swingCap = dist * 0.28;
  const biasCap  = dist * 0.22;
  const swing = clamp(40 + p.rng.range(0, 120) * curvy, 0, swingCap) * sign;
  const perpBias = clamp(p.rng.range(40, 130) * curvy, 0, biasCap);

  const cp1 = {
    x: start.x + dx * 0.33 + swing,
    y: start.y + dy * 0.33 - perpBias,
  };
  const cp2 = {
    x: start.x + dx * 0.72 - swing * 0.8,
    y: start.y + dy * 0.72 + perpBias * 0.7,
  };

  const phase1 = p.rng.range(0, Math.PI * 2);
  const jitterAmp = p.mouse.jitter * (opts.jitterScale ?? 1);

  function point(t) {
    // 양 끝 감속(smoothstep) + 미세 속도 출렁임
    const wobble = 0.05 * Math.sin(2 * Math.PI * t * 2.3 + phase1);
    const e = clamp(smoothstep(t) + wobble, 0, 1);
    const taper = Math.sin(Math.PI * e); // 양 끝 0, 중간 1
    const nx = 3.5 * Math.sin(5.2 * Math.PI * e + phase1) + 1.8 * Math.sin(13.1 * Math.PI * e);
    const ny = 3.0 * Math.cos(4.7 * Math.PI * e + phase1) + 1.8 * Math.sin(11.3 * Math.PI * e);
    return {
      x: cubic(start.x, cp1.x, cp2.x, end.x, e) + taper * nx * jitterAmp,
      y: cubic(start.y, cp1.y, cp2.y, end.y, e) + taper * ny * jitterAmp,
    };
  }

  let elapsed = 0;
  while (elapsed < duration) {
    // 폴링레이트+OS지연 흉내: 고정 간격이 아닌 로그정규 dt
    const dt = p.rng.logNormal(p.mouse.pollMs, 0.3, 2, 38);
    elapsed += dt;
    const t = clamp(elapsed / duration, 0, 1);
    const pt = point(t);
    await emitMove(send, pt.x, pt.y, button);
    await sleep(dt);
    if (t >= 1) break;
  }
  await emitMove(send, end.x, end.y, button);
}

// ============================================================
// 이동 (오버슈트 + 보정 포함)
// ============================================================

/**
 * 사람처럼 이동. 목표를 살짝 지나쳤다 보정하는 submovement 포함.
 * @param {Function} send
 * @param {string|{x,y}|bbox} target
 * @param {object} [options]
 * @param {{x,y}} [options.start]
 * @param {number} [options.duration]
 * @param {number} [options.jitter]            떨림 배율 override
 * @param {"none"|"left"|"right"|"middle"} [options.button="none"]
 * @param {boolean} [options.overshoot]        강제 on/off (기본: 페르소나 확률)
 */
export async function humanMoveTo(send, target, options = {}) {
  return withBusy(async () => {
    const p = getPersona();
    const dst = await resolveCenter(send, target);
    const start = options.start ?? cursorPos;
    const button = options.button ?? "none";

    const dx = dst.x - start.x;
    const dy = dst.y - start.y;
    const dist = Math.hypot(dx, dy);
    const totalMs = options.duration ?? p.moveDuration(dist);

    const jitterScale = options.jitter !== undefined ? options.jitter / p.mouse.jitter : 1;

    // 오버슈트: 거리가 충분하고 페르소나 확률에 걸릴 때
    const doOvershoot =
      options.overshoot ?? (dist > 140 && p.rng.bool(p.mouse.overshootProb));

    if (!doOvershoot) {
      await moveLeg(send, start, dst, totalMs, button, { jitterScale });
      return { ...cursorPos };
    }

    // 목표 너머의 오버슈트 지점 (진행 방향 + 약간의 수직 흔들림)
    const ux = dx / (dist || 1);
    const uy = dy / (dist || 1);
    const over = dist * p.mouse.overshootScale * p.rng.range(0.6, 1.4);
    const perp = p.rng.range(-1, 1) * over * 0.5;
    const overshootPt = {
      x: dst.x + ux * over - uy * perp,
      y: dst.y + uy * over + ux * perp,
    };

    // 주 동작(빠르게, 오버슈트 지점까지) + 보정(느리게, 정확히 목표로)
    await moveLeg(send, start, overshootPt, totalMs * 0.78, button, {
      jitterScale, curveScale: 1,
    });
    await sleep(p.rng.logNormal(45, 0.4, 12, 160)); // 방향 전환 직전 짧은 멈칫
    await moveLeg(send, overshootPt, dst, totalMs * 0.34, button, {
      jitterScale: jitterScale * 0.5, curveScale: 0.4,
    });

    // 가끔 한 번 더 미세 보정
    if (p.rng.bool(0.25)) {
      const tiny = { x: dst.x + p.rng.range(-2, 2), y: dst.y + p.rng.range(-2, 2) };
      await moveLeg(send, cursorPos, tiny, totalMs * 0.12, button, {
        jitterScale: 0.2, curveScale: 0.2,
      });
      await emitMove(send, dst.x, dst.y, button);
    }

    return { ...cursorPos };
  });
}

// ============================================================
// 클릭
// ============================================================

/**
 * 이동 후 클릭. 클릭 지점은 요소 안에서 가우시안 분산, press 중 미세 드리프트.
 * @param {object} [options]  humanMoveTo 옵션 +
 * @param {"left"|"right"|"middle"} [options.button="left"]
 * @param {number} [options.clickCount=1]
 */
export async function humanClick(send, target, options = {}) {
  return withBusy(async () => {
    const p = getPersona();
    const point = await resolveClickPoint(send, target);
    await humanMoveTo(send, point, options);

    const button = options.button ?? "left";
    const clickCount = options.clickCount ?? 1;

    await sleep(p.rng.logNormal(90, 0.4, 30, 320)); // 조준 후 정지

    const press = { ...cursorPos };
    await send("Input.dispatchMouseEvent", {
      type: "mousePressed",
      x: press.x, y: press.y,
      button, clickCount,
      pointerType: "mouse",
    });

    // 누르는 동안 손가락 드리프트
    await sleep(p.rng.logNormal(55, 0.45, 18, 200));
    const drift = p.rng.gaussian2D(p.mouse.pressDrift, p.mouse.pressDrift);
    const rel = { x: Math.round(press.x + drift.x), y: Math.round(press.y + drift.y) };
    if (rel.x !== press.x || rel.y !== press.y) {
      await emitMove(send, rel.x, rel.y, button);
    }

    await send("Input.dispatchMouseEvent", {
      type: "mouseReleased",
      x: rel.x, y: rel.y,
      button, clickCount,
      pointerType: "mouse",
    });

    return rel;
  });
}

// ============================================================
// 호버
// ============================================================

export async function humanHover(send, target, options = {}) {
  return withBusy(async () => {
    const p = getPersona();
    const dst = await humanMoveTo(send, target, options);
    const dwellMs = options.dwellMs ?? p.readPause(1.2);
    const radius  = options.hoverJitter ?? p.behavior.idleRadius;

    const end = Date.now() + dwellMs;
    while (Date.now() < end) {
      const off = p.rng.gaussian2D(radius, radius);
      await emitMove(send, dst.x + off.x, dst.y + off.y);
      await sleep(p.rng.logNormal(90, 0.4, 30, 260));
    }
    await emitMove(send, dst.x, dst.y);
    return dst;
  });
}

// ============================================================
// 휠 스크롤
// ============================================================

/**
 * 사람처럼 스크롤. 여러 tick으로 가속·감속, 가끔 멈춤. 간격은 로그정규.
 */
export async function humanWheel(send, deltaY, options = {}) {
  return withBusy(async () => {
    const p = getPersona();
    const deltaX = options.deltaX ?? 0;
    const pos = options.target ? await resolveCenter(send, options.target) : cursorPos;

    const totalAbs = Math.max(1, Math.hypot(deltaX, deltaY));
    const ticks = options.ticks ?? clamp(Math.ceil(totalAbs / p.rng.range(55, 90)), 4, 26);
    const totalMs = options.duration ?? p.rng.logNormal(totalAbs * 1.4 + 280, 0.25, 380, 2600);
    const pauseChance = options.pauseChance ?? 0.12;

    let sentX = 0, sentY = 0;
    const frameBase = totalMs / ticks;

    for (let i = 1; i <= ticks; i++) {
      const e = smoothstep(i / ticks);
      const tx = deltaX * e, ty = deltaY * e;
      const dx = tx - sentX, dy = ty - sentY;
      sentX = tx; sentY = ty;

      await send("Input.dispatchMouseEvent", {
        type: "mouseWheel",
        x: Math.round(pos.x), y: Math.round(pos.y),
        deltaX: Math.round(dx), deltaY: Math.round(dy),
        pointerType: "mouse",
      });

      let wait = p.rng.logNormal(frameBase, 0.3, frameBase * 0.4, frameBase * 2.2);
      if (i < ticks && p.rng.bool(pauseChance)) wait += p.rng.logNormal(320, 0.4, 140, 900);
      await sleep(wait);
    }
  });
}

// ============================================================
// 드래그
// ============================================================

export async function humanDrag(send, fromTarget, toTarget, options = {}) {
  return withBusy(async () => {
    const p = getPersona();
    const button = options.button ?? "left";
    const from = await resolveCenter(send, fromTarget);

    await humanMoveTo(send, from, options);
    await sleep(p.rng.logNormal(150, 0.4, 60, 400));

    await send("Input.dispatchMouseEvent", {
      type: "mousePressed",
      x: Math.round(from.x), y: Math.round(from.y),
      button, clickCount: 1, pointerType: "mouse",
    });
    await sleep(p.rng.logNormal(110, 0.45, 40, 360));

    // 누른 채로 곡선 이동 (드래그는 오버슈트 억제)
    const dst = await humanMoveTo(send, toTarget, {
      ...options, button, start: from, overshoot: false,
    });
    await sleep(p.rng.logNormal(120, 0.45, 50, 380));

    await send("Input.dispatchMouseEvent", {
      type: "mouseReleased",
      x: Math.round(dst.x), y: Math.round(dst.y),
      button, clickCount: 1, pointerType: "mouse",
    });
    return dst;
  });
}

// ============================================================
// idle 떨림
// ============================================================

function scheduleIdleTick() {
  if (!idleConfig) return;
  const { rng, intervalMin, intervalMax } = idleConfig;
  idleTimer = setTimeout(idleTick, rng.range(intervalMin, intervalMax));
}

async function idleTick() {
  if (!idleConfig) return;
  if (busyCount === 0) {
    const { send, rng, radius } = idleConfig;
    const off = rng.gaussian2D(radius, radius);
    try {
      await send("Input.dispatchMouseEvent", {
        type: "mouseMoved",
        x: Math.round(cursorPos.x + off.x),
        y: Math.round(cursorPos.y + off.y),
        button: "none",
        pointerType: "mouse",
      });
    } catch {}
  }
  scheduleIdleTick();
}

export function startIdleJitter(send, options = {}) {
  if (idleConfig) return;
  const p = getPersona();
  idleConfig = {
    send,
    rng: p.rng,
    radius:      options.radius      ?? p.behavior.idleRadius,
    intervalMin: options.intervalMin ?? 600,
    intervalMax: options.intervalMax ?? 2400,
  };
  scheduleIdleTick();
}

export function stopIdleJitter() {
  if (idleTimer) { clearTimeout(idleTimer); idleTimer = null; }
  idleConfig = null;
}
