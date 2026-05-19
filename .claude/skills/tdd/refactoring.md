# Refactoring

Only refactor while **green**. If a test is red, get it to green first, then refactor.

## Project-specific moves

### Extract a port

When a use case starts touching a second concern (notifications *and* persistence; cache *and* repository), extract a new port for the new concern, ship a fake with it, and inject. Don't pile responsibilities onto an existing port.

### Fake/adapter symmetry drift

After landing an integration test that caught a bug the unit tests missed:

1. Port the missing semantic into the fake.
2. Confirm a unit test now reproduces the bug against the fake.
3. Fix the adapter so the integration test passes.
4. (Optional) Promote the scenario into a contract test in `tests/<module>/contracts/` to run against both.

### `shared/` graduation

Per [`architecture.md`](../../../docs/architecture.md), code in `shared/` must be used by ≥ 2 features. While developing inside one feature, keep helpers **inside** the feature. The second consumer is the trigger to graduate, not "this looks generic."

### Import-linter contract drift

When refactoring across modules, run import-linter. Common violations:

- A new import from `features/A` into `features/B/usecases` — must go through `features/B/api`.
- A new import from `domain/` into `sqlmodel` or `fastapi` — domain is pure.
- A new import from `handlers/` into `adapters/` — must go via `deps.py`.

Fix the boundary, don't suppress the rule.

### Split an overlong use case

Signals:

- `__call__` has a top-level branch with disjoint logic per branch.
- Two unrelated command fields where each is only valid when the other is absent.
- Two integration tests describing different capabilities both go through this one use case.

Split into two `<Verb><Noun>` classes, two commands, two handlers if applicable. See [ports-and-design.md — Splitting a use case](ports-and-design.md#splitting-a-use-case).

## What to leave alone

- Working tests with awkward names (rename later, in bulk).
- Adapters with verbose SQL but correct behavior — verbosity is not a refactor signal.
- "SOLID violations" without a concrete test that's painful to write because of them.

## Re-run tests after every step

Refactor → tests → refactor → tests. Never two refactors in a row without running the suite.
