# Keyboard

`{SKILL_DIR}/scripts/human-keyboard.mjs`

Intervals are drawn from a log-normal distribution with AR(1) autocorrelation, so the
rhythm drifts the way a person's does instead of scattering uniformly. Fast sequences
roll over — the next key goes down before the previous one comes up. Hangul is composed
jamo by jamo through the IME path rather than inserted as finished text.

## Functions

| Function | Returns | Purpose |
|---|---|---|
| `humanType(send, text, opts?)` | `void` | Type a string; Latin and Hangul may be mixed freely |
| `typeChar(send, ch)` | `void` | One ASCII or symbol character |
| `typeHangulSyllable(send, syllable, opts?)` | `void` | One Hangul syllable via IME composition |
| `pressKey(send, name, modifierOpts?)` | `void` | A special key (see below) |
| `isHangulSyllable(ch)` / `syllableToSteps(s)` | | Utilities |
| `setPersona(p)` / `getPersona()` | | Persona injection and lookup |

`pressKey` covers `Enter`, `Tab`, `Backspace`, `Escape`, `Delete`, `Home`, `End`,
`PageUp`, `PageDown`, and the arrow keys.

## Options

Speed, rhythm, and typo rate come from the persona. `humanType` options are overrides.

**`humanType`**

- `typoChance: number` — probability of a typo followed by a correction (default:
  persona `typoRate`). Latin text uses adjacent-key errors and transpositions; Hangul
  uses an adjacent dubeolsik jamo, then backspace, then the correct one.
- `rollover: boolean` — key rollover on or off (default `true`)

**`pressKey` modifiers**

- `{ shift, ctrl, alt, meta }` — booleans, combined into a bitmask

## Choosing a call

| Goal | Call |
|---|---|
| Ordinary typing | `humanType(send, "Hello, 안녕")` |
| Include typos | `humanType(send, "...", { typoChance: 0.05 })` |
| Deliberate, one key at a time | `humanType(send, "...", { rollover: false })` |
| Enter / arrow key | `pressKey(send, "Enter")` / `pressKey(send, "ArrowDown")` |
| Shift+Tab | `pressKey(send, "Tab", { shift: true })` |

To change typing speed, adjust the persona's `strokesPerMin` — see `persona.md`.
Options on `humanType` deliberately do not include speed, so that one session keeps one
consistent pace.

## Notes

- **Hangul keydown reports `keyCode: 229` and `key: "Process"`.** That is what a real
  OS-level IME sends. A page trying to read jamo out of `event.key` sees nothing — the
  same as with genuine IME input. Such pages must listen on `composition*` events.
- **Standalone compatibility jamo and emoji fall back to `Input.insertText`.**
  `isHangulSyllable` returns false for them, so no `composition*` events fire.
- **Focus first.** Click the field with `humanClick` before typing; input events go to
  whatever currently holds focus.
- **Character shortcuts need a custom event.** `pressKey` only knows the special-key
  table, so combinations like Ctrl+A require dispatching `Input.dispatchKeyEvent`
  directly.
