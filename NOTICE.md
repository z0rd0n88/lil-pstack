# NOTICE

lil-pstack is a lean subset fork of [pstack-claude](https://github.com/michael-denyer/pstack-claude), itself an MIT-licensed Claude Code port of Cursor's pstack and cursor-team-kit plugins. This fork copies 22 skills and one agent verbatim from pstack-claude's `plugins/pstack/` (version 0.9.15), then edits their prose to remove references to skills this fork doesn't include (the `poteto-mode` router and its hook, the 20 `principle-*` skills, `arena`, `swarm`, `architect`, `tdd`, `automate-me`, `typescript-best-practices`, `technical-writing`) and to point `Models` sections at this repo's own trimmed `models.json`. All upstream copyright notices are preserved below.

## Sources

| Files in this repo | Upstream source | License file |
| --- | --- | --- |
| `skills/{how,why,interrogate,reflect,show-me-your-work,figure-it-out,create-verification-skill,maintain-verification-skill,no-comments,bro,unslop}/`, `agents/comment-sicko.md` | [pstack-claude @ 0.9.15](https://github.com/michael-denyer/pstack-claude), (c) 2026 Lauren Tan | [LICENSE-pstack-claude](LICENSE-pstack-claude) |
| `skills/{babysit,recall,blast-radius,setup-pstack}/` | Independently authored within the [pstack-claude](https://github.com/michael-denyer/pstack-claude) port (no upstream Cursor equivalent) | [LICENSE-pstack-claude](LICENSE-pstack-claude) |
| `skills/{fix-ci,fix-merge-conflicts,get-pr-comments,make-pr-easy-to-review,deslop,thermo-nuclear-code-quality-review,what-did-i-get-done}/` | pstack-claude's port of Cursor's `cursor-team-kit`, (c) 2026 Cursor | [LICENSE-cursor-team-kit](LICENSE-cursor-team-kit) |
| `.claude-plugin/marketplace.json`, `plugins/lil-pstack/.claude-plugin/plugin.json`, `plugins/lil-pstack/models.json`, this file, `README.md` | Authored for this fork | [LICENSE](LICENSE) |

## What changed from pstack-claude

- Dropped: the `poteto-mode` router skill and its auto-firing `SessionStart` hook, all 20 `principle-*` skills, and `arena`/`swarm`/`architect`/`tdd`/`automate-me`/`typescript-best-practices`/`technical-writing`. No plugin-level hook fires on session start; every skill here is invoked directly (`/skill-name` or the Skill tool), never by a forced router.
- Dropped Codex support: every "Platform note" paragraph pointing at `codex-tools.md` is removed, since this fork ships Claude Code only.
- Edited: cross-references to the dropped skills were rewritten as plain prose (e.g. "run the `arena` skill" became "ask several models in parallel `Agent` calls") so the guidance still stands without naming a skill that isn't here. See each skill's git history in this repo for the exact diff against upstream.
- `models.json` trimmed from 18 roles to the 8 used by the four included panel/investigation skills (`how`, `why`, `reflect`, `interrogate`).
- Per the MIT license, modifications are permitted; all upstream copyright notices are preserved in the LICENSE* files above.
