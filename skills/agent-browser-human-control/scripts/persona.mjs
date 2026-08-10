// persona.mjs
// 한 세션 = 한 사람. 세션 시드로부터 일관된 "성향"을 만든다.
//
// 왜 필요한가: 동작마다 독립 난수를 쓰면 "매 클릭이 다른 사람"처럼 보인다.
// 실제 사람은 세션 내내 비슷한 속도·곡선 성향·오타율·리듬을 유지한다.
// 페르소나는 그 성향 파라미터 묶음 + 전용 RNG를 들고 다닌다.

import { createRng, makeAR1, clamp } from "./human-random.mjs";

/**
 * 페르소나 생성.
 * @param {string|number} [seed]  생략 시 매번 다른 사람. 지정 시 재현 가능.
 * @returns {object} persona
 */
export function createPersona(seed) {
  const rng = createRng(seed);
  const r = (lo, hi) => rng.range(lo, hi);

  // ── 마우스 성향 ──────────────────────────────
  const mouse = {
    // 거리당 이동 시간 계수(ms/px). 사람마다 손 빠르기가 다름
    msPerPx: r(1.7, 2.8),
    minDuration: r(280, 420),
    maxDuration: r(1500, 2100),
    // 곡선이 휘는 정도
    curviness: r(0.7, 1.4),
    // 이동 중 미세 떨림 강도
    jitter: r(0.7, 1.3),
    // 목표를 지나쳤다 되돌아오는 경향
    overshootProb: r(0.25, 0.6),
    overshootScale: r(0.04, 0.12), // 거리 대비 오버슈트 비율
    // 클릭 정밀도: 요소 크기 대비 표준편차(작을수록 정확)
    clickPrecision: r(0.16, 0.28),
    // 누르는 동안 손가락 드리프트(px)
    pressDrift: r(0.6, 1.8),
    // 폴링레이트 흉내: 이벤트 간 평균 간격(ms). 125Hz~품질에 따라
    pollMs: r(6, 11),
  };

  // ── 키보드 성향 ──────────────────────────────
  // 분당 타건 수(한국식 "타"). 영문 1글자=1타, 한글 자모 1개=1타
  const strokesPerMin = r(420, 490);
  // 키 누름 유지 시간 중앙값
  const holdMedian = r(38, 66);
  // 타건당 목표 시간 = 60000/strokesPerMin. 여기서 hold를 빼고, gapAfter가
  // 배율·간헐 정지·로그정규로 평균이 부푸는 몫(≈1.25)을 나눠 간격 중앙값을 역산.
  // (계수 1.25는 벤치로 보정한 값)
  const keyboard = {
    strokesPerMin,
    baseWpm: strokesPerMin, // 하위호환(데모 표시용)
    baseDelay: clamp((60000 / strokesPerMin - holdMedian) / 1.4, 22, 360),
    holdMedian,
    // 간격 리듬의 자기상관 강도
    rhythmRho: r(0.3, 0.55),
    rhythmSigma: r(0.26, 0.42),
    // 빠른 연타 시 롤오버(이전 키 떼기 전에 다음 키 누름) 확률
    rolloverProb: r(0.12, 0.34),
    // 오타율과 유형 분포
    typoRate: r(0.0, 0.05),
    // 가끔 "생각하는" 긴 정지
    pauseChance: r(0.015, 0.05),
    // 구두점 뒤 추가 호흡 배율
    punctPause: r(1.4, 2.4),
    // 단어 사이(공백) 호흡 배율 — burst-pause 패턴
    spaceBurst: r(1.3, 1.7),
  };

  // ── 행동(고수준) 성향 ────────────────────────
  const behavior = {
    // 폼 필드/요소를 "읽는" 시간 중앙값(ms)
    readMedian: r(350, 900),
    // 동작 사이 기본 텀
    betweenActions: r(180, 480),
    // idle 떨림 반경
    idleRadius: r(1.5, 3.5),
  };

  // 키 간격 리듬 생성기 (AR1) — 세션 내 상태 유지
  const typingRhythm = makeAR1(rng, keyboard.baseDelay, {
    rho: keyboard.rhythmRho,
    sigma: keyboard.rhythmSigma,
    min: keyboard.baseDelay * 0.35,
    max: keyboard.baseDelay * 3.5,
  });

  return {
    seed: rng.seed,
    rng,
    mouse,
    keyboard,
    behavior,
    typingRhythm,

    /** 거리 → 이동 시간(ms), 페르소나 속도 + 로그정규 변동 */
    moveDuration(dist) {
      const base = dist * mouse.msPerPx + 180;
      return rng.logNormal(base, 0.22, mouse.minDuration, mouse.maxDuration);
    },

    /** 요소를 읽는 시간 */
    readPause(scale = 1) {
      return rng.logNormal(behavior.readMedian * scale, 0.4, 80, 4000);
    },

    /** 동작 사이 텀 */
    actionGap(scale = 1) {
      return rng.logNormal(behavior.betweenActions * scale, 0.35, 60, 3000);
    },
  };
}
