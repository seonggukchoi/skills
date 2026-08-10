# agent-browser-human-control

Maintainer notes for this skill. The skill itself is `SKILL.md`; this file is not loaded
into the agent's context.

## Layout

```
SKILL.md          entry point, kept thin — routes to references/
references/       loaded on demand, one file per topic
scripts/          vendored upstream modules, not written here
```

## Vendored code

`scripts/` is a verbatim copy of six modules from an upstream repository.

| | |
|---|---|
| Upstream | <https://github.com/seonggukchoi/human-control.js> |
| Pinned commit | `0eef3ebc0913830e0fe639da85764af40c78cc33` (2026-06-23) |
| Files | `human-mouse.mjs`, `human-keyboard.mjs`, `human-touch.mjs`, `human-random.mjs`, `persona.mjs`, `stealth.mjs` |

Copied rather than pulled in as an npm package. `npx skills` already copies a skill
directory to the install target and refreshes it with `npx skills update`, so a package
dependency would add a second install step at exactly the moment the skill runs — and a
failure mode wherever the network or install permissions are restricted. The modules
have no runtime dependencies and import each other by relative path, so a plain copy
runs as-is.

The Korean comments inside `scripts/` are upstream's. They are kept unchanged so a
synced copy stays byte-identical to its source and drift can be checked mechanically.
Everything written for this skill — `SKILL.md`, `references/`, this file — is English.

## Keeping it current

Two things drift independently, and only one of them is mechanical.

### Code — copy

```sh
git clone --depth 1 https://github.com/seonggukchoi/human-control.js /tmp/human-control

# check whether anything actually changed
for f in human-mouse human-keyboard human-touch human-random persona stealth; do
  cmp -s "/tmp/human-control/$f.mjs" "skills/agent-browser-human-control/scripts/$f.mjs" \
    || echo "changed: $f.mjs"
done

# if it did, copy and record the new commit
cp /tmp/human-control/{human-mouse,human-keyboard,human-touch,human-random,persona,stealth}.mjs \
   skills/agent-browser-human-control/scripts/
git -C /tmp/human-control rev-parse HEAD    # update the pinned commit above
```

Run from the repository root. Never edit `scripts/` directly — a sync overwrites it, and
the change is lost silently. Fixes belong upstream.

### Docs — read and reconcile

`references/*.md` are an English rewrite of upstream's `AGENTS.md`, not a copy, so no
tool will tell you when they fall behind. After syncing code, diff the upstream guide
over the same range and reconcile by hand:

```sh
git -C /tmp/human-control diff <pinned-commit>..HEAD -- AGENTS.md
```

Watch for changed function signatures, renamed or added options, and new modules. A new
module also needs a row in `SKILL.md`'s module table and a routing entry under "Where to
go next", or the agent will never find it.

## Notes

- `SKILL.md` stays thin on purpose: it is always in context once the skill triggers,
  while `references/` is only read when relevant. Detail belongs in the references.
- Examples use `{SKILL_DIR}` as a placeholder for the skill's own directory, since the
  install path differs per agent and per machine.
- Upstream ships a demo, a benchmark, and tests that are not vendored here — they need
  Playwright and a browser download, which a skill should not assume. Clone upstream to
  run them.
