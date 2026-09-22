---
name: deslop
description: Remove AI-generated code slop and clean up code style
menu-description: deslop a diff before commit
---

# Remove AI code slop

Check the diff against main and remove AI-generated slop introduced in the branch.

## Focus Areas

- Extra comments that are unnecessary or inconsistent with local style
- Comments written to answer a review finding rather than to inform the next reader
- Defensive checks or try/catch blocks that are abnormal for trusted code paths
- Casts to `any` used only to bypass type issues
- Deeply nested code that should be simplified with early returns
- Other patterns inconsistent with the file and surrounding codebase

### The provenance test

Comment density is a weak signal — a branch can sit right at the density of its
neighbours and still be full of slop. Ask where each comment came from instead.

A comment written while fixing a review finding is addressed to the reviewer, not
to whoever reads the file next. It restates the guard below it, argues that a
function deserves to exist, or explains why a finding was closed. The commit
message is where that belongs. These cluster in branches that went through a
review-and-fix round, and they read as thorough, which is why they survive.

**Keep any comment stating a fact the code cannot state.** That an API path
resolves more than one kind of object, why a cache key deliberately omits a
field, which of two orderings is load-bearing. The test is not length or tone:
delete the ones that argue, keep the ones that inform.

## Guardrails

- Keep behavior unchanged unless fixing a clear bug.
- Prefer minimal, focused edits over broad rewrites.
- Keep the final summary concise (1-3 sentences).
