// human-keyboard.mjs (v2)
// CDP로 사람처럼 키보드 입력을 시뮬레이션한다.
//
// v2 개선점:
//   - 페르소나 연동: 세션 = 한 사람. WPM/리듬/오타율/롤오버 성향이 일관됨
//   - 로그정규 + AR(1) 리듬: 균등분포 대신 사람의 간격 분포 + 자기상관(리듬)
//   - 키 롤오버: 빠른 연타 시 이전 키를 떼기 전에 다음 키를 누름(down1 down2 up1 up2)
//   - digraph hold: 키 누름 시간이 키마다 다름(같은 손 연속은 느림 근사)
//   - 오타 다양화: 인접 키 오타 + transposition(순서 바뀜) 후 정정
//   - 한글: 두벌식 자모 IME 조합(keyCode 229 + imeSetComposition + insertText) 유지
//   - 숫자/기호는 약간 느리게
//
// send = (method, params) => Promise.

import { createPersona } from "./persona.mjs";
import { clamp } from "./human-random.mjs";

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// ============================================================
// 페르소나
// ============================================================

let activePersona = null;
export function setPersona(persona) { activePersona = persona; }
export function getPersona() {
  if (!activePersona) activePersona = createPersona();
  return activePersona;
}

// ============================================================
// modifiers / 키 매핑
// ============================================================

function mods({ shift, ctrl, alt, meta } = {}) {
  return (alt ? 1 : 0) | (ctrl ? 2 : 0) | (meta ? 4 : 0) | (shift ? 8 : 0);
}

const SYM = {
  " ":  { code: "Space",        kc: 32  },
  "-":  { code: "Minus",        kc: 189 },
  "=":  { code: "Equal",        kc: 187 },
  "[":  { code: "BracketLeft",  kc: 219 },
  "]":  { code: "BracketRight", kc: 221 },
  "\\": { code: "Backslash",    kc: 220 },
  ";":  { code: "Semicolon",    kc: 186 },
  "'":  { code: "Quote",        kc: 222 },
  ",":  { code: "Comma",        kc: 188 },
  ".":  { code: "Period",       kc: 190 },
  "/":  { code: "Slash",        kc: 191 },
  "`":  { code: "Backquote",    kc: 192 },
};
const SHIFTED = {
  "!":"1","@":"2","#":"3","$":"4","%":"5","^":"6","&":"7","*":"8","(":"9",")":"0",
  "_":"-","+":"=","{":"[","}":"]","|":"\\",":":";",'"':"'","<":",",">":".","?":"/","~":"`",
};

// 키가 속한 손 (롤오버/리듬 근사용). l=왼손, r=오른손
const HAND = {};
"qwertasdfgzxcvb12345".split("").forEach((c) => (HAND[c] = "l"));
"yuiophjklnm67890".split("").forEach((c) => (HAND[c] = "r"));

function charToKey(ch) {
  if (/^[a-z]$/.test(ch)) return { key: ch, code: `Key${ch.toUpperCase()}`, kc: ch.toUpperCase().charCodeAt(0), text: ch };
  if (/^[A-Z]$/.test(ch)) return { key: ch, code: `Key${ch}`, kc: ch.charCodeAt(0), text: ch, shift: true };
  if (/^[0-9]$/.test(ch)) return { key: ch, code: `Digit${ch}`, kc: ch.charCodeAt(0), text: ch };
  if (SYM[ch])     return { key: ch, ...SYM[ch], text: ch };
  if (SHIFTED[ch]) {
    const base = SHIFTED[ch];
    const info = SYM[base] ?? { code: `Digit${base}`, kc: base.charCodeAt(0) };
    return { key: ch, ...info, text: ch, shift: true };
  }
  return { insertOnly: true, text: ch };
}

const SPECIAL = {
  Enter:      { code: "Enter",      kc: 13, text: "\r" },
  Tab:        { code: "Tab",        kc: 9,  text: "\t" },
  Backspace:  { code: "Backspace",  kc: 8  },
  Delete:     { code: "Delete",     kc: 46 },
  Escape:     { code: "Escape",     kc: 27 },
  ArrowLeft:  { code: "ArrowLeft",  kc: 37 },
  ArrowRight: { code: "ArrowRight", kc: 39 },
  ArrowUp:    { code: "ArrowUp",    kc: 38 },
  ArrowDown:  { code: "ArrowDown",  kc: 40 },
  Home:       { code: "Home",       kc: 36 },
  End:        { code: "End",        kc: 35 },
  PageUp:     { code: "PageUp",     kc: 33 },
  PageDown:   { code: "PageDown",   kc: 34 },
};

// ============================================================
// 한글 자모 / 두벌식
// ============================================================

const HANGUL_BASE = 0xAC00;
const HANGUL_LAST = 0xD7A3;

const CHO  = "ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ".split("");
const JUNG = "ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ".split("");
const JONG = ["", ..."ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ".split("")];

const JUNG_COMPOUND = {
  "ㅘ":["ㅗ","ㅏ"], "ㅙ":["ㅗ","ㅐ"], "ㅚ":["ㅗ","ㅣ"],
  "ㅝ":["ㅜ","ㅓ"], "ㅞ":["ㅜ","ㅔ"], "ㅟ":["ㅜ","ㅣ"],
  "ㅢ":["ㅡ","ㅣ"],
};
const JONG_COMPOUND = {
  "ㄳ":["ㄱ","ㅅ"], "ㄵ":["ㄴ","ㅈ"], "ㄶ":["ㄴ","ㅎ"],
  "ㄺ":["ㄹ","ㄱ"], "ㄻ":["ㄹ","ㅁ"], "ㄼ":["ㄹ","ㅂ"],
  "ㄽ":["ㄹ","ㅅ"], "ㄾ":["ㄹ","ㅌ"], "ㄿ":["ㄹ","ㅍ"],
  "ㅀ":["ㄹ","ㅎ"], "ㅄ":["ㅂ","ㅅ"],
};
const JUNG_REV = Object.fromEntries(Object.entries(JUNG_COMPOUND).map(([k, v]) => [v.join(""), k]));
const JONG_REV = Object.fromEntries(Object.entries(JONG_COMPOUND).map(([k, v]) => [v.join(""), k]));

const DUBEOLSIK = {
  "ㄱ":{code:"KeyR",kc:82}, "ㄴ":{code:"KeyS",kc:83}, "ㄷ":{code:"KeyE",kc:69},
  "ㄹ":{code:"KeyF",kc:70}, "ㅁ":{code:"KeyA",kc:65}, "ㅂ":{code:"KeyQ",kc:81},
  "ㅅ":{code:"KeyT",kc:84}, "ㅇ":{code:"KeyD",kc:68}, "ㅈ":{code:"KeyW",kc:87},
  "ㅊ":{code:"KeyC",kc:67}, "ㅋ":{code:"KeyZ",kc:90}, "ㅌ":{code:"KeyX",kc:88},
  "ㅍ":{code:"KeyV",kc:86}, "ㅎ":{code:"KeyG",kc:71},
  "ㄲ":{code:"KeyR",kc:82,shift:true}, "ㄸ":{code:"KeyE",kc:69,shift:true},
  "ㅃ":{code:"KeyQ",kc:81,shift:true}, "ㅆ":{code:"KeyT",kc:84,shift:true},
  "ㅉ":{code:"KeyW",kc:87,shift:true},
  "ㅏ":{code:"KeyK",kc:75}, "ㅑ":{code:"KeyI",kc:73}, "ㅓ":{code:"KeyJ",kc:74},
  "ㅕ":{code:"KeyU",kc:85}, "ㅗ":{code:"KeyH",kc:72}, "ㅛ":{code:"KeyY",kc:89},
  "ㅜ":{code:"KeyN",kc:78}, "ㅠ":{code:"KeyB",kc:66}, "ㅡ":{code:"KeyM",kc:77},
  "ㅣ":{code:"KeyL",kc:76}, "ㅐ":{code:"KeyO",kc:79}, "ㅔ":{code:"KeyP",kc:80},
  "ㅒ":{code:"KeyO",kc:79,shift:true}, "ㅖ":{code:"KeyP",kc:80,shift:true},
};

export function isHangulSyllable(ch) {
  const c = ch.charCodeAt(0);
  return c >= HANGUL_BASE && c <= HANGUL_LAST;
}

export function syllableToSteps(syllable) {
  const code    = syllable.charCodeAt(0) - HANGUL_BASE;
  const choIdx  = Math.floor(code / 588);
  const jungIdx = Math.floor((code % 588) / 28);
  const jongIdx = code % 28;

  const steps = [CHO[choIdx]];
  const jungSeq = JUNG_COMPOUND[JUNG[jungIdx]] ?? [JUNG[jungIdx]];
  let acc = "";
  for (const j of jungSeq) {
    acc += j;
    const cur = JUNG.includes(acc) ? acc : JUNG_REV[acc];
    steps.push(String.fromCharCode(HANGUL_BASE + choIdx * 588 + JUNG.indexOf(cur) * 28));
  }
  if (jongIdx > 0) {
    const jongSeq = JONG_COMPOUND[JONG[jongIdx]] ?? [JONG[jongIdx]];
    let jacc = "";
    for (const j of jongSeq) {
      jacc += j;
      const cur = JONG.includes(jacc) ? jacc : JONG_REV[jacc];
      steps.push(String.fromCharCode(HANGUL_BASE + choIdx * 588 + jungIdx * 28 + JONG.indexOf(cur)));
    }
  }
  return steps;
}

// ============================================================
// 오타 시뮬레이션
// ============================================================

const NEIGHBORS = {
  a:"sqwz", b:"vghn", c:"xdfv", d:"serfcx", e:"wsdr", f:"drtgvc", g:"ftyhbv",
  h:"gyujnb", i:"ujko", j:"huiknm", k:"jiolm", l:"kop", m:"njk", n:"bhjm",
  o:"iklp", p:"ol", q:"wa", r:"edft", s:"awedxz", t:"rfgy", u:"yhji",
  v:"cfgb", w:"qase", x:"zsdc", y:"tghu", z:"asx",
};
function neighborTypo(rng, ch) {
  const pool = NEIGHBORS[ch.toLowerCase()];
  if (!pool) return null;
  const pick = pool[Math.floor(rng.next() * pool.length)];
  return ch === ch.toUpperCase() ? pick.toUpperCase() : pick;
}

// 두벌식 자판에서 물리적으로 인접한 초성/중성(한글 오타용)
const CHO_NEIGHBOR = {
  "ㅂ":"ㅈ", "ㅈ":"ㅂㄷ", "ㄷ":"ㅈㄱ", "ㄱ":"ㄷㅅ", "ㅅ":"ㄱ",
  "ㅁ":"ㄴ", "ㄴ":"ㅁㅇ", "ㅇ":"ㄴㄹ", "ㄹ":"ㅇㅎ", "ㅎ":"ㄹ",
  "ㅋ":"ㅌ", "ㅌ":"ㅋㅊ", "ㅊ":"ㅌㅍ", "ㅍ":"ㅊ",
};
const JUNG_NEIGHBOR = {
  "ㅛ":"ㅕ", "ㅕ":"ㅛㅑ", "ㅑ":"ㅕㅐ", "ㅐ":"ㅑㅔ", "ㅔ":"ㅐ",
  "ㅗ":"ㅓ", "ㅓ":"ㅗㅏ", "ㅏ":"ㅓㅣ", "ㅣ":"ㅏ",
  "ㅠ":"ㅜ", "ㅜ":"ㅠㅡ", "ㅡ":"ㅜ",
};

/**
 * 한글 음절의 초성 또는 중성 하나를 두벌식 인접 자모로 바꿔 "오타 음절"을 만든다.
 * 복합 모음/받침 등 인접맵에 없으면 null(오타 생략).
 */
function hangulTypoSyllable(rng, syllable) {
  const code = syllable.charCodeAt(0) - HANGUL_BASE;
  let cho  = Math.floor(code / 588);
  let jung = Math.floor((code % 588) / 28);
  const jong = code % 28;

  if (rng.bool()) {
    const cand = CHO_NEIGHBOR[CHO[cho]];
    if (!cand) return null;
    const idx = CHO.indexOf(cand[Math.floor(rng.next() * cand.length)]);
    if (idx < 0) return null;
    cho = idx;
  } else {
    const cand = JUNG_NEIGHBOR[JUNG[jung]];
    if (!cand) return null;
    const idx = JUNG.indexOf(cand[Math.floor(rng.next() * cand.length)]);
    if (idx < 0) return null;
    jung = idx;
  }
  const wrong = String.fromCharCode(HANGUL_BASE + cho * 588 + jung * 28 + jong);
  return wrong === syllable ? null : wrong;
}

// ============================================================
// 저수준 키 이벤트
// ============================================================

function keyBase(info, modifiers) {
  return {
    key: info.key, code: info.code,
    windowsVirtualKeyCode: info.kc, nativeVirtualKeyCode: info.kc,
    modifiers,
  };
}

async function sendKeyDown(send, info) {
  const modifiers = mods({ shift: info.shift });
  await send("Input.dispatchKeyEvent", {
    ...keyBase(info, modifiers), type: "keyDown",
    text: info.text, unmodifiedText: info.text,
  });
}
async function sendKeyUp(send, info) {
  const modifiers = mods({ shift: info.shift });
  await send("Input.dispatchKeyEvent", { ...keyBase(info, modifiers), type: "keyUp" });
}

/** ASCII/기호 한 글자 (down + hold + up). 비ASCII는 insertText. */
export async function typeChar(send, ch) {
  const p = getPersona();
  const info = charToKey(ch);
  if (info.insertOnly) { await send("Input.insertText", { text: ch }); return; }
  await sendKeyDown(send, info);
  await sleep(p.rng.logNormal(p.keyboard.holdMedian, 0.32, 22, 200));
  await sendKeyUp(send, info);
}

/** 특수 키 한 번 누름 */
export async function pressKey(send, name, modifierOpts = {}) {
  const p = getPersona();
  const s = SPECIAL[name];
  if (!s) throw new Error(`unknown key: ${name}`);
  const modifiers = mods(modifierOpts);
  const base = {
    key: name, code: s.code,
    windowsVirtualKeyCode: s.kc, nativeVirtualKeyCode: s.kc,
    modifiers,
  };
  await send("Input.dispatchKeyEvent", {
    ...base, type: "keyDown",
    ...(s.text ? { text: s.text, unmodifiedText: s.text } : {}),
  });
  await sleep(p.rng.logNormal(p.keyboard.holdMedian * 0.8, 0.3, 20, 160));
  await send("Input.dispatchKeyEvent", { ...base, type: "keyUp" });
}

// ============================================================
// 한글 음절 (IME 조합)
// ============================================================

export async function typeHangulSyllable(send, syllable, opts = {}) {
  const p = getPersona();
  const gap = opts.gap ?? (() => p.typingRhythm());

  const code    = syllable.charCodeAt(0) - HANGUL_BASE;
  const choIdx  = Math.floor(code / 588);
  const jungIdx = Math.floor((code % 588) / 28);
  const jongIdx = code % 28;

  const jamos = [CHO[choIdx]];
  jamos.push(...(JUNG_COMPOUND[JUNG[jungIdx]] ?? [JUNG[jungIdx]]));
  if (jongIdx > 0) {
    const jong = JONG[jongIdx];
    jamos.push(...(JONG_COMPOUND[jong] ?? [jong]));
  }
  const steps = syllableToSteps(syllable);

  for (let i = 0; i < jamos.length; i++) {
    const jamo = jamos[i];
    const k = DUBEOLSIK[jamo];
    if (!k) continue;
    const modifiers = mods({ shift: k.shift });

    await send("Input.dispatchKeyEvent", {
      type: "keyDown", key: "Process", code: k.code,
      windowsVirtualKeyCode: 229, nativeVirtualKeyCode: 229, modifiers,
    });
    await send("Input.imeSetComposition", {
      text: steps[i], selectionStart: steps[i].length, selectionEnd: steps[i].length,
    });
    await sleep(p.rng.logNormal(p.keyboard.holdMedian * 0.9, 0.32, 18, 150));
    await send("Input.dispatchKeyEvent", {
      type: "keyUp", key: jamo, code: k.code,
      windowsVirtualKeyCode: k.kc, nativeVirtualKeyCode: k.kc, modifiers,
    });

    if (i < jamos.length - 1) await sleep(gap() * 1.05);
  }
  await send("Input.insertText", { text: syllable });
}

// ============================================================
// 고수준 타이핑
// ============================================================

function isFastAscii(ch) {
  return /^[a-zA-Z]$/.test(ch);
}

/** 다음 글자까지 간격 계산 (리듬 + 문맥) */
function gapAfter(p, ch) {
  let delay = p.typingRhythm();
  if (/[.!?]/.test(ch))      delay *= p.keyboard.punctPause;
  else if (/[,;:)]/.test(ch)) delay *= (1 + (p.keyboard.punctPause - 1) * 0.5);
  if (/[0-9]/.test(ch))      delay *= 1.25;           // 숫자열은 느림
  if (SHIFTED[ch] || SYM[ch]) delay *= 1.15;          // 기호도 느림
  if (ch === " ")            delay *= p.keyboard.spaceBurst; // 단어 사이 호흡(burst-pause)
  if (p.rng.bool(p.keyboard.pauseChance)) delay += p.rng.logNormal(600, 0.4, 280, 1400);
  return delay;
}

/**
 * 사람처럼 텍스트를 타이핑한다.
 * @param {Function} send
 * @param {string} text
 * @param {object} [opts]
 * @param {number} [opts.typoChance]   override (기본: 페르소나 typoRate)
 * @param {boolean} [opts.rollover]    롤오버 on/off (기본: 페르소나)
 */
export async function humanType(send, text, opts = {}) {
  const p = getPersona();
  const typoChance = opts.typoChance ?? p.keyboard.typoRate;
  const allowRollover = opts.rollover ?? true;

  // 보류된 keyUp (롤오버: 다음 키 down 직후에 떼기 위해)
  let pendingUp = null;
  const flushPending = async () => {
    if (pendingUp) { await sendKeyUp(send, pendingUp); pendingUp = null; }
  };

  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    const next = text[i + 1];

    // ── 한글 ──
    if (isHangulSyllable(ch)) {
      await flushPending();
      // 한글 오타: 인접 자모로 잘못 친 음절 → 인지 → 백스페이스(음절 삭제) → 정타
      if (typoChance > 0 && p.rng.bool(typoChance * 0.7)) {
        const wrong = hangulTypoSyllable(p.rng, ch);
        if (wrong) {
          await typeHangulSyllable(send, wrong);
          await sleep(p.rng.logNormal(340, 0.4, 160, 720)); // 알아챔
          await pressKey(send, "Backspace");
          await sleep(p.rng.logNormal(120, 0.4, 50, 280));
        }
      }
      await typeHangulSyllable(send, ch);
      await sleep(gapAfter(p, ch));
      continue;
    }
    // ── 줄바꿈 / 탭 ──
    if (ch === "\n") { await flushPending(); await pressKey(send, "Enter"); await sleep(gapAfter(p, ch) + p.rng.logNormal(160, 0.4, 80, 500)); continue; }
    if (ch === "\t") { await flushPending(); await pressKey(send, "Tab");   await sleep(gapAfter(p, ch)); continue; }

    // ── transposition 오타: 인접 두 글자 순서 바꿔 치고 정정 ──
    if (typoChance > 0 && isFastAscii(ch) && isFastAscii(next) && ch !== next &&
        p.rng.bool(typoChance * 0.4)) {
      await flushPending();
      await typeChar(send, next);                       // 순서 바꿔서
      await sleep(p.typingRhythm() * 0.7);
      await typeChar(send, ch);
      await sleep(p.rng.logNormal(320, 0.4, 160, 700)); // 알아챔
      await pressKey(send, "Backspace");
      await sleep(p.rng.logNormal(90, 0.4, 40, 220));
      await pressKey(send, "Backspace");
      await sleep(p.rng.logNormal(140, 0.4, 60, 320));
      await typeChar(send, ch);                          // 올바르게 다시
      await sleep(p.typingRhythm() * 0.7);
      await typeChar(send, next);
      await sleep(gapAfter(p, next));
      i++; // next까지 소비
      continue;
    }

    // ── 인접 키 오타 후 정정 ──
    if (typoChance > 0 && isFastAscii(ch) && p.rng.bool(typoChance)) {
      const typo = neighborTypo(p.rng, ch);
      if (typo) {
        await flushPending();
        await typeChar(send, typo);
        await sleep(p.rng.logNormal(360, 0.4, 170, 760));
        await pressKey(send, "Backspace");
        await sleep(p.rng.logNormal(110, 0.4, 50, 260));
      }
    }

    // ── 일반 ASCII: 롤오버 고려 ──
    const info = charToKey(ch);
    if (info.insertOnly) {
      await flushPending();
      await send("Input.insertText", { text: ch });
      await sleep(gapAfter(p, ch));
      continue;
    }

    const rollover =
      allowRollover && isFastAscii(ch) && isFastAscii(next) &&
      HAND[ch.toLowerCase()] !== HAND[(next || "").toLowerCase()] && // 다른 손일 때 더 자연스러운 롤오버
      p.rng.bool(p.keyboard.rolloverProb);

    await sendKeyDown(send, info);
    // 이전 보류 키를 지금(현재 down 직후) 떼면 down1→down2→up1 패턴
    await flushPending();

    if (rollover) {
      // 현재 키 up을 보류 → 다음 글자 down 이후에 떼짐(겹침)
      await sleep(p.rng.logNormal(p.keyboard.holdMedian * 0.5, 0.3, 14, 110));
      pendingUp = info;
      await sleep(gapAfter(p, ch) * 0.55); // 롤오버는 간격 짧음
    } else {
      await sleep(p.rng.logNormal(p.keyboard.holdMedian, 0.32, 22, 200));
      await sendKeyUp(send, info);
      await sleep(gapAfter(p, ch));
    }
  }
  await flushPending();
}
