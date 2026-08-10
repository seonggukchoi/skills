// human-touch.mjs
// CDP로 사람처럼 "터치"한다 — 탭/스와이프/플릭/롱프레스.
//
// 왜 별도 모듈인가:
//   human-mouse.mjs는 `Input.dispatchMouseEvent`만 쓴다. 그런데 모바일 페이지의
//   일부 요소는 mouse가 아니라 `touchstart/touchend`에만 리스너를 단다(키패드 등).
//   그런 요소엔 mouse 좌표가 아무리 정확해도 입력이 들어가지 않는다.
//   이 모듈은 `Input.dispatchTouchEvent` 기반으로 그 경로를 채운다.
//
// 두 겹이 필요하다:
//   1) 컨텍스트를 touch-capable로 — `enableTouch(send)` (navigator.maxTouchPoints>0,
//      'ontouchstart' in window === true). 페이지가 touch 지원을 feature-detect하면
//      이게 없으면 touch UI 자체가 안 뜨거나 입력을 거른다.
//   2) 실제 터치 시퀀스 — touchStart → (touchMove) → touchEnd.
//
// 좌표계는 CSS 픽셀(viewport 기준). send = (method, params) => Promise.

import { createPersona } from "./persona.mjs";
import { clamp } from "./human-random.mjs";
import { getElementBox } from "./human-mouse.mjs";

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function cubic(p0, p1, p2, p3, t) {
  const u = 1 - t;
  return u*u*u*p0 + 3*u*u*t*p1 + 3*u*t*t*p2 + t*t*t*p3;
}
function smoothstep(t) { return t * t * (3 - 2 * t); }

// ============================================================
// 모듈 상태
// ============================================================

let activePersona = null;
let busyCount     = 0;
let lastTouch     = { x: 100, y: 100 };
let touchEnabled  = false;

export function setPersona(persona) { activePersona = persona; }
export function getPersona() {
  if (!activePersona) activePersona = createPersona();
  return activePersona;
}
export function getLastTouch() { return { ...lastTouch }; }
export function isTouchEnabled() { return touchEnabled; }

async function withBusy(fn) {
  busyCount++;
  try { return await fn(); }
  finally { busyCount--; }
}

// ============================================================
// touch-capable 컨텍스트
// ============================================================

/**
 * 브라우저 컨텍스트를 touch-capable로 만든다. page.goto 이전이든 이후든 호출 가능하나,
 * 페이지가 로드 시점에 touch 지원을 검사한다면 goto **전에** 호출하는 게 안전하다.
 * Playwright라면 newContext({ hasTouch: true, isMobile: true })가 더 근본적이다.
 *
 * @param {Function} send
 * @param {object} [opts]
 * @param {number}  [opts.maxTouchPoints=1]   navigator.maxTouchPoints 노출값
 * @param {boolean} [opts.emitForMouse=false] mouse 이벤트를 touch로도 변환(보강용)
 */
export async function enableTouch(send, opts = {}) {
  const maxTouchPoints = opts.maxTouchPoints ?? 1;
  await send("Emulation.setTouchEmulationEnabled", { enabled: true, maxTouchPoints });
  if (opts.emitForMouse) {
    // mouse 입력도 touch로 변환. 직접 dispatchTouchEvent를 쓸 거면 보통 불필요.
    await send("Emulation.setEmitTouchEventsForMouse", { enabled: true, configuration: "mobile" });
  }
  touchEnabled = true;
}

export async function disableTouch(send) {
  await send("Emulation.setTouchEmulationEnabled", { enabled: false });
  touchEnabled = false;
}

// ============================================================
// 좌표 해석
// ============================================================

// target: selector(string) | {x,y} | bbox객체 → 탭 지점.
//   - {x,y} 직접 좌표는 그대로 쓴다(작은 키처럼 정밀이 중요한 곳에 권장).
//   - selector/bbox는 요소 안에서 작게 분산(기본은 마우스 클릭보다 훨씬 좁게).
async function resolveTapPoint(send, target, opts = {}) {
  const p = getPersona();
  let box = null;
  if (typeof target === "string") box = await getElementBox(send, target);
  else if (target && typeof target.width === "number") box = target;

  if (!box) {
    // 직접 좌표 — 분산하지 않는다.
    if (target && typeof target.cx === "number") return { x: target.cx, y: target.cy };
    return { x: target.x, y: target.y };
  }

  // 손가락은 마우스보다 부정확하지만, 작은 키를 노릴 땐 분산을 좁힌다.
  const spread = opts.spread ?? 0.5;                 // clickPrecision에 곱하는 축소 계수
  const sdX = (box.width  / 2) * p.mouse.clickPrecision * spread;
  const sdY = (box.height / 2) * p.mouse.clickPrecision * spread;
  const off = p.rng.gaussian2D(sdX, sdY);
  return {
    x: clamp(box.cx + off.x, box.x + 2, box.x + box.width  - 2),
    y: clamp(box.cy + off.y, box.y + 2, box.y + box.height - 2),
  };
}

// 단일 터치포인트 생성(반경·압력에 사람다운 미세 변동)
function makePoint(p, x, y, id = 0) {
  const radiusX = clamp(9 + p.rng.gaussian() * 2.5, 4, 18);
  const radiusY = clamp(radiusX * p.rng.range(0.85, 1.15), 4, 20);
  const force   = clamp(0.45 + p.rng.gaussian() * 0.12, 0.15, 0.95);
  return {
    x: Math.round(x), y: Math.round(y),
    radiusX: Math.round(radiusX), radiusY: Math.round(radiusY),
    rotationAngle: 0, force, id,
  };
}

// ============================================================
// 탭
// ============================================================

/**
 * 사람처럼 탭한다. touchStart → (짧은 접촉 + 미세 드리프트) → touchEnd.
 * @param {Function} send
 * @param {string|{x,y}|bbox} target
 * @param {object} [opts]
 * @param {number}  [opts.holdMs]    접촉 유지 시간 중앙값(ms). 기본 페르소나 기반
 * @param {number}  [opts.spread]    selector/bbox일 때 분산 축소 계수(기본 0.5)
 * @param {boolean} [opts.drift]     접촉 중 미세 이동 on/off(기본 확률)
 * @returns {{x,y}} 탭 좌표
 */
export async function humanTap(send, target, opts = {}) {
  return withBusy(async () => {
    const p = getPersona();
    const pt = await resolveTapPoint(send, target, opts);
    const id = 0;

    // touchStart (최소 1포인트 필수)
    await send("Input.dispatchTouchEvent", {
      type: "touchStart",
      touchPoints: [makePoint(p, pt.x, pt.y, id)],
    });

    // 접촉 유지 — 사람 탭은 보통 50~120ms
    const holdMedian = opts.holdMs ?? clamp(p.keyboard.holdMedian * 1.3, 45, 140);
    await sleep(p.rng.logNormal(holdMedian, 0.32, 28, 240));

    // 누르는 동안 손가락 미세 드리프트(접촉면 흔들림)
    const doDrift = opts.drift ?? p.rng.bool(0.5);
    if (doDrift) {
      const d = p.rng.gaussian2D(p.mouse.pressDrift, p.mouse.pressDrift);
      await send("Input.dispatchTouchEvent", {
        type: "touchMove",
        touchPoints: [makePoint(p, pt.x + d.x, pt.y + d.y, id)],
      });
      await sleep(p.rng.logNormal(24, 0.4, 8, 90));
    }

    // touchEnd (CDP 규약: touchEnd/touchCancel은 touchPoints가 비어야 함)
    await send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });

    lastTouch = { x: Math.round(pt.x), y: Math.round(pt.y) };
    return { ...lastTouch };
  });
}

/** 길게 누르기 (컨텍스트 메뉴 등). 기본 600ms 접촉. */
export async function humanLongPress(send, target, opts = {}) {
  return humanTap(send, target, { ...opts, holdMs: opts.holdMs ?? 600, drift: opts.drift ?? true });
}

// ============================================================
// 스와이프 / 플릭
// ============================================================

/**
 * 누른 채로 곡선 이동 후 뗀다. 스크롤·캐러셀·드래그형 UI에.
 * @param {Function} send
 * @param {string|{x,y}|bbox} from
 * @param {string|{x,y}|bbox} to
 * @param {object} [opts]
 * @param {number} [opts.duration]   총 이동 시간 ms (기본 거리 비례)
 * @param {number} [opts.steps]      touchMove 횟수 (기본 거리 비례)
 * @param {number} [opts.curviness]  곡률 배율 (기본 페르소나)
 */
export async function humanSwipe(send, from, to, opts = {}) {
  return withBusy(async () => {
    const p = getPersona();
    const a = await resolveTapPoint(send, from, { spread: 0 });
    const b = await resolveTapPoint(send, to,   { spread: 0 });
    const id = 0;

    const dx = b.x - a.x, dy = b.y - a.y;
    const dist = Math.hypot(dx, dy);
    const duration = opts.duration ?? clamp(dist * p.mouse.msPerPx * 0.7 + 160, 160, 1400);
    const steps    = opts.steps    ?? clamp(Math.round(dist / 14), 6, 40);

    // 가벼운 곡률 — 직선 스와이프는 봇 신호
    const curvy = (opts.curviness ?? p.mouse.curviness);
    const sign  = p.rng.bool() ? -1 : 1;
    const swing = clamp(p.rng.range(8, 36) * curvy, 0, dist * 0.25) * sign;
    const cp1 = { x: a.x + dx * 0.33 + swing,      y: a.y + dy * 0.33 - swing * 0.4 };
    const cp2 = { x: a.x + dx * 0.66 - swing * 0.7, y: a.y + dy * 0.66 + swing * 0.3 };

    await send("Input.dispatchTouchEvent", {
      type: "touchStart",
      touchPoints: [makePoint(p, a.x, a.y, id)],
    });
    await sleep(p.rng.logNormal(40, 0.4, 14, 140)); // 접촉 후 출발 직전 정지

    for (let i = 1; i <= steps; i++) {
      const e = smoothstep(i / steps);
      const x = cubic(a.x, cp1.x, cp2.x, b.x, e) + p.rng.gaussian() * 0.8;
      const y = cubic(a.y, cp1.y, cp2.y, b.y, e) + p.rng.gaussian() * 0.8;
      await send("Input.dispatchTouchEvent", {
        type: "touchMove",
        touchPoints: [makePoint(p, x, y, id)],
      });
      await sleep(p.rng.logNormal(duration / steps, 0.3, 4, 120));
    }

    await send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
    lastTouch = { x: Math.round(b.x), y: Math.round(b.y) };
    return { ...lastTouch };
  });
}

/**
 * 터치로 스크롤 — 손가락을 위/아래로 미는 스와이프. deltaY>0이면 콘텐츠가 위로
 * 올라감(아래로 스크롤)이라, 손가락은 그 반대 방향으로 민다.
 * @param {number} deltaY  스크롤할 거리 px (양수=아래로 스크롤)
 */
export async function humanTouchScroll(send, deltaY, opts = {}) {
  const p = getPersona();
  const center = opts.target
    ? await resolveTapPoint(send, opts.target, { spread: 0 })
    : { x: lastTouch.x, y: lastTouch.y };
  // 한 번에 너무 길면 여러 번 플릭으로 나눈다(화면 높이 ~70% 단위)
  const screenSpan = opts.span ?? 480;
  const dir = deltaY >= 0 ? -1 : 1;          // 아래로 스크롤 → 손가락은 위로
  let remaining = Math.abs(deltaY);
  while (remaining > 1) {
    const seg = Math.min(remaining, screenSpan * p.rng.range(0.6, 0.9));
    const from = { x: center.x + p.rng.gaussian() * 6, y: center.y };
    const to   = { x: center.x + p.rng.gaussian() * 6, y: center.y + dir * seg };
    await humanSwipe(send, from, to, { duration: opts.duration });
    remaining -= seg;
    if (remaining > 1) await sleep(p.rng.logNormal(180, 0.4, 70, 600)); // 플릭 사이 호흡
  }
}
