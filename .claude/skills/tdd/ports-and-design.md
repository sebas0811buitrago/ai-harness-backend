# Ports and design

The project's hexagonal layout already encodes two ideas: small intent-revealing interfaces (**deep modules**), and design for **testability**. Both converge on the port.

See [`module-structure.md` — Use cases](../../../docs/architecture/module-structure.md#use-cases).

## Deep modules behind shallow ports

A good port has a small surface and hides substantial behavior behind it:

- **Shallow port**: `record_payment(payment: Payment) -> Receipt`
- **Deep adapter**: writes to Postgres, emits an outbox event, updates a denormalized read model.

The use case knows only about `record_payment`. Adapter complexity is invisible. Tests against the fake are short and behavior-shaped.

**Anti-pattern**: a port with many methods that mirror SQL operations. `get`, `update`, `save`, `delete_by_filter` is a leaky abstraction — the use case is now reasoning about persistence, not capability.

## Port naming = use-case verbs, not CRUD

- ✅ `mark_settled`, `record_payment`, `reserve_seat`, `next_unprocessed_event`
- ❌ `update_status`, `insert`, `find_all`, `list_by`

`module-structure.md` already requires this. The rule exists because CRUD names re-couple the use case to a storage shape and make fakes drift into mini-ORMs.

## Command / query objects

`usecases/commands.py` carries frozen Pydantic commands. Use them aggressively:

- **One command per use case.** Multi-argument `__call__` signatures drift; a `Command` doesn't.
- **Carry `Principal` as a field** when the actor matters — never pull it from request state inside the use case.
- **Add fields at the boundary**, not inside. A new optional field flows through one schema → one command field; no signature changes anywhere.

## Dependency injection via `deps.py`

Use cases take ports as keyword-only constructor args. Wiring lives in `deps.py`:

- One factory per port, one per use case.
- One `<Port>Dep` / `<UseCase>Dep` `Annotated` alias per dependency.
- Handlers depend on the alias, never on the port type directly.

For tests, integration tests override factories via `app.dependency_overrides`. Unit tests construct the use case directly with fakes — no FastAPI involvement.

## Splitting a use case

If a use case acquires a second `__call__` overload, two distinct return shapes, or branches on a flag at the top of `__call__` and proceeds down disjoint paths — it's two use cases. Split. The tests get sharper and the ports get smaller.
