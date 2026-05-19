# Fakes

The project uses **hand-rolled in-memory fakes** in `usecases/ports/_fakes.py` for the unit tier. `AsyncMock` and any mocking framework are **banned**.

See [`module-structure.md` — Use cases](../../../docs/architecture/module-structure.md#use-cases).

## Rules

1. **Every port ships with a fake from day one.** A new port without a fake is incomplete.
2. **Fakes mirror port *semantics*, not adapter *implementation*.** A `save` that returns the persisted entity must do the same in the fake; a `find_by_id` that raises `NotFoundError` on miss must do the same in the fake.
3. **Tests do not inspect fake internals.** Asserting on `fake._items[x]` couples the test to the fake's storage; assert through the port's public read methods instead.
4. **Fakes are deterministic.** No clocks, no randomness, no I/O. Injectable seeds / IDs / clocks only.
5. **One fake per port, not per test.** Add a constructor or a `with_existing(...)` classmethod for arrangement instead of subclassing in test files.

## If you reach for a mock, the port is the wrong shape

When you want to write `mock.call_args` or `mock.assert_called_with(...)`, the port is exposing implementation, not capability. Symptoms:

- Port has CRUD method names (`save`, `update`, `delete`) instead of intent (`record_payment`, `mark_settled`).
- Port returns `None` and the test wants to verify a side-effect happened — promote the return to a domain value the use case can act on, or expose a read method the test can use.
- The test needs to assert *that* a method was called but not *what* the system did — that's wiring, not behavior.

Fix the port, then write the test against a fake. See [ports-and-design.md](ports-and-design.md).

## Fake/adapter symmetry drift

Over time, fakes diverge from adapters as adapters gain real-world behavior the fake doesn't reproduce (case-insensitive matching, ordering, optimistic-concurrency conflicts, unique constraints). Two countermeasures:

1. **Contract tests** — a shared pytest module that runs the same scenarios against both the fake and the real adapter. Lives in `tests/<module>/contracts/`. The real-adapter run uses testcontainers.
2. When an integration test catches a bug the unit tests missed, **port the missing semantic into the fake first**, then make the unit test reproduce the bug, then fix the adapter. This keeps the fake honest going forward.
