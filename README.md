# lil-pstack

A lean personal fork of [pstack-claude](https://github.com/michael-denyer/pstack-claude): 22 hand-picked skills plus the `comment-sicko` agent, no auto-injecting router hook, no `principle-*` bloat.

## Why this exists

pstack-claude ships 50+ skills and a `SessionStart` hook that injects a mandate to route every non-trivial task through its `poteto-mode` router. That's a lot of always-on context and ceremony for skills used occasionally. lil-pstack keeps the skills worth having and drops the rest: no router, no hook, no `principle-*` skills, no Codex support.

## What's included

- **PR shepherding:** `babysit`, `fix-ci`, `fix-merge-conflicts`, `get-pr-comments`, `make-pr-easy-to-review`
- **Context and safety:** `recall`, `blast-radius`, `reflect`, `what-did-i-get-done`
- **Subsystem understanding:** `how`, `why`
- **Review:** `interrogate`, `no-comments`, `thermo-nuclear-code-quality-review`, `deslop`, `bro`
- **Prose:** `unslop` (strip AI-writing tells)
- **Verification scaffolding:** `create-verification-skill`, `maintain-verification-skill`
- **Long/audited work:** `figure-it-out`, `show-me-your-work`
- **Setup:** `setup-pstack` (configures per-role model overrides in `~/.claude/pstack-models.md`)

Each skill is invoked directly (`/skill-name`, or the Skill tool) — nothing here fires automatically on session start.

## Install

```
/plugin marketplace add z0rd0n88/lil-pstack
/plugin install lil-pstack@lil-pstack
```

Then run `/setup-pstack` once to configure per-role model overrides.

## Provenance

Skills are copied from pstack-claude with light edits to remove references to the router, hook, and skills this fork doesn't carry. Full attribution and license mapping: [NOTICE.md](NOTICE.md).
