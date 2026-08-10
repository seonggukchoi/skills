// stealth.mjs
// 입력을 아무리 사람처럼 만들어도, 브라우저가 "자동화됨"이라고 광고하면 소용없다.
// 가장 흔히 검사되는 자동화 신호를 새 문서마다 주입 스크립트로 가린다.
//
// 한계(정직하게): 상용 안티봇(DataDome, HUMAN 등)은 수백 개 신호를 종합한다.
// 이 패치는 navigator.webdriver 류의 1차 신호를 덮을 뿐, 만능이 아니다.
// 진지한 용도라면 puppeteer-extra-plugin-stealth / playwright-extra를 권장.
//
// 사용:
//   import { applyStealth, STEALTH_LAUNCH_ARGS } from "./stealth.mjs";
//   const browser = await chromium.launch({ args: STEALTH_LAUNCH_ARGS });
//   await applyStealth(page);   // page.goto 전에 호출

// 자동화 흔적을 줄이는 실행 인자
export const STEALTH_LAUNCH_ARGS = [
  "--disable-blink-features=AutomationControlled",
  "--no-default-browser-check",
  "--no-first-run",
  "--disable-infobars",
];

// 브라우저 컨텍스트에서 실행될 패치. 새 문서마다 가장 먼저 돈다.
function stealthScript() {
  // 1) navigator.webdriver 제거
  try {
    Object.defineProperty(Navigator.prototype, "webdriver", {
      get: () => false,
      configurable: true,
    });
  } catch {}

  // 2) window.chrome 흉내 (헤드리스엔 보통 없음)
  try {
    if (!window.chrome) {
      window.chrome = { runtime: {}, app: { isInstalled: false }, csi: () => {}, loadTimes: () => {} };
    }
  } catch {}

  // 3) languages / plugins 가 비면 의심받음
  try {
    Object.defineProperty(navigator, "languages", {
      get: () => ["ko-KR", "ko", "en-US", "en"],
      configurable: true,
    });
  } catch {}
  try {
    if (!navigator.plugins || navigator.plugins.length === 0) {
      const fake = [
        { name: "Chrome PDF Plugin" },
        { name: "Chrome PDF Viewer" },
        { name: "Native Client" },
      ];
      Object.defineProperty(navigator, "plugins", {
        get: () => fake,
        configurable: true,
      });
    }
  } catch {}

  // 4) permissions.query 가 자동화에서 일관적이지 않은 값을 반환하는 문제
  try {
    const orig = navigator.permissions && navigator.permissions.query;
    if (orig) {
      navigator.permissions.query = (params) =>
        params && params.name === "notifications"
          ? Promise.resolve({ state: Notification.permission })
          : orig.call(navigator.permissions, params);
    }
  } catch {}

  // 5) WebGL vendor/renderer 가 SwiftShader/llvmpipe 면 헤드리스 신호
  try {
    const proto = WebGLRenderingContext && WebGLRenderingContext.prototype;
    if (proto) {
      const getParam = proto.getParameter;
      proto.getParameter = function (p) {
        if (p === 37445) return "Intel Inc.";                    // UNMASKED_VENDOR_WEBGL
        if (p === 37446) return "Intel Iris OpenGL Engine";      // UNMASKED_RENDERER_WEBGL
        return getParam.call(this, p);
      };
    }
  } catch {}

  // 6) chrome 자동화 전역 흔적 정리
  try {
    for (const k of Object.keys(window)) {
      if (/^cdc_/.test(k) || /\$cdc_/.test(k)) delete window[k];
    }
  } catch {}
}

/**
 * Playwright page/context에 stealth 주입 스크립트를 건다. page.goto 전에 호출.
 * @param {import('playwright').Page|import('playwright').BrowserContext} target
 */
export async function applyStealth(target) {
  await target.addInitScript(stealthScript);
}

/**
 * CDP 직접 사용 시: Page.addScriptToEvaluateOnNewDocument 로 주입.
 * @param {Function} send  (method, params) => Promise
 */
export async function applyStealthCDP(send) {
  const source = `(${stealthScript.toString()})();`;
  await send("Page.addScriptToEvaluateOnNewDocument", { source });
}
