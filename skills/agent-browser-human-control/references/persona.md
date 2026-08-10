# Persona

`{SKILL_DIR}/scripts/persona.mjs`

One session equals one person. Drawing independent randomness per action makes every
click look like a different individual; a real person keeps a recognizable speed, path
curvature, typo rate, and rhythm for as long as they are at the keyboard. A persona is
that bundle of traits plus a dedicated RNG, derived from a single seed.

```js
const persona = createPersona(seed?);   // omit the seed for a different person each run
```

Passing a seed makes the run reproducible, which is what demos, recordings, and
regression comparisons need.

## What it holds

| Path | Meaning |
|---|---|
| `persona.seed` | Resolved 32-bit seed |
| `persona.rng` | Dedicated RNG: `range`, `int`, `bool`, `pick`, `gaussian`, `normal`, `logNormal`, `gaussian2D` |
| `persona.mouse` | `msPerPx`, `minDuration`, `maxDuration`, `curviness`, `jitter`, `overshootProb`, `overshootScale`, `clickPrecision`, `pressDrift`, `pollMs` |
| `persona.keyboard` | `strokesPerMin`, `baseDelay`, `holdMedian`, `rhythmRho`, `rhythmSigma`, `rolloverProb`, `typoRate`, `pauseChance`, `punctPause`, `spaceBurst` |
| `persona.behavior` | `readMedian`, `betweenActions`, `idleRadius` |
| `persona.moveDuration(dist)` | Distance → travel time in ms |
| `persona.readPause(scale?)` / `persona.actionGap(scale?)` | Reading pause / gap between actions |
| `persona.typingRhythm()` | AR(1) interval generator that carries state across the session |

## Adjusting traits

The object is plain and mutable, so change it after creation and inject it as usual.
Typing speed is measured in strokes per minute — one Latin character or one Hangul jamo
counts as one stroke. The default range is roughly 420–490.

```js
const p = createPersona("session-1");
p.keyboard.strokesPerMin = 600;
p.keyboard.baseDelay = 60000 / 600 - p.keyboard.holdMedian;   // keep the two in sync
mouse.setPersona(p);
kbd.setPersona(p);
```

`baseDelay` has to be recomputed because it is derived from `strokesPerMin` at creation
time; setting the rate alone leaves the actual intervals unchanged.

To shift the range for every session instead of one, edit `scripts/persona.mjs` — but
note that this is vendored upstream code, so the change is reverted the next time the
scripts are synced. See `../README.md`.
