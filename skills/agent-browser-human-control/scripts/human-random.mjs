// human-random.mjs
// 사람다운 타이밍/좌표를 위한 난수·분포 유틸.
//   - 시드 가능한 PRNG (mulberry32) → 페르소나 재현·세션 일관성
//   - 균등분포 대신 사람의 반응시간에 맞는 로그정규/가우시안
//   - AR(1) 과정 → 키 간격의 리듬(자기상관)
//
// 핵심 아이디어: Math.random()의 균등분포는 히스토그램을 뜨면 봇 신호가 된다.
// 사람의 간격은 평균 근처에 몰리고 가끔 긴 꼬리를 갖는 로그정규에 가깝다.

const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));

/** 32비트 시드 PRNG. 같은 시드 → 같은 수열. */
function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** 문자열/숫자 → 32비트 시드 해시 */
export function hashSeed(input) {
  if (typeof input === "number") return input >>> 0;
  const str = String(input ?? "");
  let h = 2166136261 >>> 0;
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

/**
 * 시드 기반 난수 생성기. 모든 분포 헬퍼를 갖는다.
 * seed를 생략하면 비결정적(Math.random 기반) 시드를 만든다 — 단, 한 번 만든 인스턴스는 일관됨.
 */
export function createRng(seed) {
  const resolvedSeed =
    seed === undefined
      ? hashSeed(`${Math.floor(Math.random() * 0xffffffff)}-${Date.now()}`)
      : hashSeed(seed);

  const next = mulberry32(resolvedSeed);

  // Box-Muller용 캐시
  let spare = null;

  const rng = {
    seed: resolvedSeed,

    /** [0,1) 균등 */
    next,

    /** [lo,hi) 균등 실수 */
    range: (lo, hi) => lo + next() * (hi - lo),

    /** [lo,hi] 균등 정수 */
    int: (lo, hi) => Math.floor(lo + next() * (hi - lo + 1)),

    /** 확률 p로 true */
    bool: (p = 0.5) => next() < p,

    /** 배열에서 하나 */
    pick: (arr) => arr[Math.floor(next() * arr.length)],

    /** 표준정규 N(0,1) */
    gaussian() {
      if (spare !== null) {
        const v = spare;
        spare = null;
        return v;
      }
      let u, v, s;
      do {
        u = next() * 2 - 1;
        v = next() * 2 - 1;
        s = u * u + v * v;
      } while (s >= 1 || s === 0);
      const mul = Math.sqrt((-2 * Math.log(s)) / s);
      spare = v * mul;
      return u * mul;
    },

    /** 평균 mean, 표준편차 sd 정규 (선택적 [min,max] 절단) */
    normal(mean, sd, min = -Infinity, max = Infinity) {
      return clamp(mean + sd * rng.gaussian(), min, max);
    },

    /**
     * 로그정규. median 근처에 몰리고 오른쪽 꼬리가 긴다 — 사람 간격/지연에 적합.
     * @param {number} median  중앙값(ms 등)
     * @param {number} sigma   로그공간 표준편차(0.3~0.5 권장)
     */
    logNormal(median, sigma = 0.35, min = 0, max = Infinity) {
      return clamp(median * Math.exp(sigma * rng.gaussian()), min, max);
    },

    /** 2D 가우시안 오프셋 — 클릭 위치 분산 등 */
    gaussian2D(sdX, sdY = sdX) {
      return { x: rng.gaussian() * sdX, y: rng.gaussian() * sdY };
    },
  };

  return rng;
}

/**
 * AR(1) 과정: nextValue = mean + rho * (prev - mean) + noise.
 * rho가 클수록(0~1) 이전 값과 강하게 상관 → "리듬". 키 간격에 사용.
 *
 * @param {object} rng        createRng 인스턴스
 * @param {number} median     중앙값
 * @param {object} [opts]
 * @param {number} [opts.rho=0.4]    자기상관 강도
 * @param {number} [opts.sigma=0.3]  로그공간 노이즈
 * @param {number} [opts.min=0]
 * @param {number} [opts.max=Infinity]
 */
export function makeAR1(rng, median, opts = {}) {
  const rho = opts.rho ?? 0.4;
  const sigma = opts.sigma ?? 0.3;
  const min = opts.min ?? 0;
  const max = opts.max ?? Infinity;

  // 로그공간에서 AR(1)을 돌려 곱셈적 변동을 만든다
  const logMedian = Math.log(median);
  let logPrev = logMedian;

  return function nextInterval(scale = 1) {
    const noise = sigma * rng.gaussian();
    logPrev = logMedian + rho * (logPrev - logMedian) + noise;
    return clamp(Math.exp(logPrev) * scale, min, max);
  };
}

export { clamp };
