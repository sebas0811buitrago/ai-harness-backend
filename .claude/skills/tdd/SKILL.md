---
name: tdd
description: Test-driven development with red-green-refactor loop. Use when the user wants to build a feature or fix a bug test-first, mentions TDD or red-green-refactor, or asks for unit/integration tests inside a feature module.
---

# Test-Driven Development

This skill is the TDD discipline layered on top of the project's architecture. The project's *what* — ports, fakes, two-tier tests, error mapping — is documented in:

- [`docs/architecture.md`](../../../docs/architecture.md)
- [`docs/architecture/module-structure.md`](../../../docs/architecture/module-structure.md)
- [`docs/architecture/conventions.md`](../../../docs/architecture/conventions.md)

This skill carries only the TDD *how*. Read the docs for the rules; read this skill for the loop.

## Philosophy

Tests verify **observable behavior through the use case's or handler's public surface**, never internal collaborator wiring. Code can change entirely; tests shouldn't.

- **Good test**: instantiates a use case with its fakes, sends a command, asserts on the returned domain result or raised domain error. Reads like a capability statement.
- **Bad test**: reaches into the fake's internal dict, asserts on adapter method calls, or verifies a side-effect through an out-of-band channel.

See [tests.md](tests.md) for examples and the unit-vs-integration decision rule. See [fakes.md](fakes.md) for the fake-per-port rule and why `AsyncMock` is banned.

## Anti-pattern: horizontal slices

**Do not write all tests first, then all implementation.** This produces tests of *imagined* behavior — shapes, signatures — not actual capability. They pass when behavior breaks and break when behavior is fine.

Work vertically:

```
WRONG (horizontal):
  RED:   test1, test2, test3, test4
  GREEN: impl1, impl2, impl3, impl4

RIGHT (vertical):
  RED→GREEN: test1→impl1
  RED→GREEN: test2→impl2
  ...
```

Each test responds to what the previous cycle revealed.

## Workflow

### 1. Planning

Use vocabulary from the feature's `domain/entities.py` and `usecases/commands.py` so test names and interface vocabulary match the project's language.

- [ ] Identify the use case (one business operation → one `<Verb><Noun>` class — see [`module-structure.md` — Use cases](../../../docs/architecture/module-structure.md#use-cases))
- [ ] Define the port shape — use-case-driven method names, not CRUD
- [ ] Sketch the in-memory fake alongside the port; both ship together (`usecases/ports/_fakes.py`)
- [ ] Define the command/query (frozen Pydantic; `Principal` field if the actor matters)
- [ ] List observable behaviors to test at the **unit** tier
- [ ] List HTTP / persistence / cross-module behaviors to test at the **integration** tier
- [ ] Confirm with the user which behaviors matter most before red-green starts

See [ports-and-design.md](ports-and-design.md) for port and command/query design.

### 2. Tracer bullet

One test → one implementation. End-to-end through the chosen tier's public surface.

```
RED:   Write the test for the first behavior → fails
GREEN: Minimal code to pass → passes
```

### 3. Incremental loop

For each remaining behavior:

```
RED:   Write next test → fails
GREEN: Minimal code to pass → passes
```

Rules:

- One test at a time.
- Only enough code to pass the current test.
- Don't anticipate future tests.
- Tests assert on outcomes (return value, raised domain error, persisted state via the public read path, HTTP response), never on internals.

### 4. Refactor (only while green)

After tests pass, look for project-specific refactor moves: port extraction, fake/adapter symmetry drift, `shared/` graduation, import-linter contract drift. See [refactoring.md](refactoring.md).

**Never refactor while red.** Get to green first.

## Per-cycle checklist

```
[ ] Test describes a capability, not implementation
[ ] Test uses the use case's __call__ or the HTTP endpoint — not adapter internals
[ ] Test would survive an internal refactor
[ ] Code is minimal for this test
[ ] No speculative features added
```
