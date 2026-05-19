# PRD: Todos CRUD API

## Problem Statement

The project currently has a flat, non-production dummy structure (`main.py`, `models.py`, `database.py`, a single `Item` model) that does not reflect the intended modular-monolith architecture described in the project conventions. There is no real feature, no shared infrastructure, no authentication concept, and no test strategy in place. Developers cannot use the repo as a meaningful harness for building new capabilities because there is no idiomatic baseline to build from.

## Solution

Bootstrap the full modular-monolith skeleton as defined in `docs/architecture/` and `docs/architecture/conventions.md`, using a Todos CRUD API as the first real feature. The skeleton provides shared infrastructure (error handling, pagination, auth, logging, settings) that all future features inherit. The Todos feature exercises every layer of the architecture — domain entity, use cases, port/adapter, HTTP handler, migrations, and tests — producing a working, deployable API that also serves as the canonical reference implementation for the project.

## User Stories

1. As a developer, I want a bootstrapped `src/app/` composition root, so that I have a well-structured entry point that wires middleware, error handlers, and feature modules in a predictable order.
2. As a developer, I want shared domain error base classes (`NotFoundError`, `ConflictError`, `ValidationError`, `UnauthorizedError`, `ForbiddenError`), so that any feature can raise typed domain errors without knowing HTTP status codes.
3. As a developer, I want a shared RFC 9457 Problem error handler registered on the app, so that all domain errors are automatically serialised into `application/problem+json` responses with correct status codes, without any per-route boilerplate.
4. As a developer, I want `RequestValidationError` reshaped into a `Problem` response with an `errors` extension listing field paths, so that API consumers get consistent, structured validation feedback.
5. As a developer, I want a `ListEnvelope[T]` type and opaque cursor helpers in `shared/http/pagination`, so that any feature can implement cursor-based list endpoints without re-implementing encoding, decoding, or limit clamping.
6. As a developer, I want a shared `Principal` model and `get_current_principal` dependency in `shared/auth`, so that every route that requires identity gets a consistent, typed actor object without knowing the auth mechanism.
7. As a developer, I want bearer-token dummy auth (`Authorization: Bearer <username>` → `Principal(id=username)`), so that owner-scoped behaviour can be exercised in development and tests without a real auth system.
8. As a developer, I want a missing or blank `Authorization` header to return a 401 Problem response, so that unauthenticated access is rejected consistently at the dependency level.
9. As a developer, I want structlog configured in the app lifespan (JSON in production, console-dev format otherwise), so that all log output is structured and follows the `<domain>.<action>[.<outcome>]` event naming convention.
10. As a developer, I want import-linter contracts enforcing the documented dependency rules, so that accidental cross-layer or cross-module imports are caught in CI.
11. As an API consumer, I want to create a todo by posting a title and optional description, so that I can record tasks I need to complete.
12. As an API consumer, I want the create response to include a `Location` header pointing to the new todo, so that I can navigate directly to the created resource without parsing the body.
13. As an API consumer, I want to list my todos with cursor-based pagination, so that I can efficiently retrieve large numbers of todos without offset drift.
14. As an API consumer, I want the list response wrapped in a `ListEnvelope` with a `next_cursor` field, so that I know whether more items exist and how to fetch them.
15. As an API consumer, I want to filter my todo list by completion status (`?completed=true|false`), so that I can view only open or only finished todos.
16. As an API consumer, I want todos in the list sorted by creation time descending by default, so that my most recently added todos appear first.
17. As an API consumer, I want to retrieve a single todo by ID, so that I can view its full details.
18. As an API consumer, I want a 404 Problem response when I request a todo that does not exist or belongs to another owner, so that I cannot discover other users' data.
19. As an API consumer, I want to partially update a todo (title, description, completed) via PATCH, so that I can toggle completion or rename a todo without resending unchanged fields.
20. As an API consumer, I want the `updated_at` timestamp to reflect the time of each update, so that I can track when a todo was last modified.
21. As an API consumer, I want to delete a todo by ID and receive a 204 response, so that I can remove completed or unwanted tasks.
22. As an API consumer, I want a 422 Problem response with field-level error details when I submit an invalid request body, so that I can fix my request without guessing which field is wrong.
23. As an API consumer, I want each todo to carry `created_at` and `updated_at` timestamps in ISO 8601 format, so that I can display or sort by time in a client application.
24. As a developer, I want the todos feature to live in its own Postgres schema (`todos`), so that the module owns its data boundary and migrations are isolated.
25. As a developer, I want Alembic set up with an initial migration creating the `todos.todo` table, so that the schema is version-controlled and reproducible.
26. As a developer, I want a `TodoRepository` Protocol port with an in-memory fake, so that use cases can be unit-tested without a database.
27. As a developer, I want one use-case class per operation (`CreateTodo`, `ListTodos`, `GetTodo`, `UpdateTodo`, `DeleteTodo`), so that each business operation is independently testable and replaceable.
28. As a developer, I want every use case to accept a `Principal` in its command, so that owner-scoping is enforced uniformly inside the hexagon rather than scattered across handlers.
29. As a developer, I want integration tests for every route using real Postgres via testcontainers, so that the full stack is verified without mocks.
30. As a developer, I want tests named using the EARS convention (`test_when_<event>_<endpoint>_shall_<response>` / `test_if_<unwanted>_<endpoint>_shall_<response>`), so that test intent is immediately readable without looking at the body.
31. As a developer, I want the dummy flat files (`main.py`, `models.py`, `database.py`, `Item`, `test_main.py`) removed, so that the repo contains only the canonical modular structure and there is no confusion about which pattern to follow.

## Implementation Decisions

### Architecture
- The project follows a **modular monolith** built on FastAPI, with features as **hexagonal, vertically-sliced** modules. Each module owns its domain, use cases, adapters, handlers, migrations, and public surface (`api.py`).
- Dependency rule enforced by import-linter: `handlers → deps → usecases → ports ← adapters`; `domain` is a pure sink; no framework imports in `domain` or `usecases`.

### Module breakdown

**Shared infrastructure (new)**
- `shared/auth` — `Principal(id: str)` frozen Pydantic model; `get_current_principal` FastAPI dependency that parses `Authorization: Bearer <token>` and maps the token value to `Principal.id`. Raises `UnauthorizedError` on missing/blank header.
- `shared/errors` — Abstract base classes: `NotFoundError`, `ConflictError`, `ValidationError`, `UnauthorizedError`, `ForbiddenError`. No HTTP status codes here.
- `shared/http/error_handlers` — Maps the shared error base classes to RFC 9457 Problem responses. Reshapes `RequestValidationError` into a Problem with `status=422` and an `errors` extension containing field paths. Exposes a `register(app)` function called by the composition root.
- `shared/http/pagination` — `ListEnvelope[T]` generic response model; opaque cursor encode/decode (base64 of `"<iso_created_at>|<id>"`); `clamp_limit(limit, default=20, max=100)` helper. Pure functions, no I/O.
- `shared/config` — Base settings class using `pydantic-settings`; `DATABASE_URL` and environment detection.
- `shared/logging` — structlog configuration: JSON renderer in production, console renderer in development. Bound in app lifespan.

**Todos feature (new)**
- `features/todos/domain` — `Todo` entity (frozen Pydantic `BaseModel`, `extra="forbid"`): `id: int`, `owner_id: str`, `title: str`, `description: str | None`, `completed: bool`, `created_at: datetime`, `updated_at: datetime`. `TodoNotFound` error inheriting `NotFoundError`.
- `features/todos/usecases/ports` — `TodoRepository` Protocol: `add(todo_data) → Todo`, `get_for_owner(id, owner_id) → Todo` (raises `TodoNotFound` if missing or wrong owner), `list_for_owner(owner_id, completed, cursor, limit) → tuple[list[Todo], str | None]`, `update(id, owner_id, patch) → Todo`, `delete_for_owner(id, owner_id) → None`. In-memory fake (`InMemoryTodoRepository`) in `_fakes.py`.
- `features/todos/usecases` — Five use-case classes, one per file: `CreateTodo`, `ListTodos`, `GetTodo`, `UpdateTodo`, `DeleteTodo`. Each has `__init__(*, repo: TodoRepository)` and `async def __call__(self, cmd: <Command>)`. Commands are frozen Pydantic models carrying `principal: Principal`.
- `features/todos/adapters/db` — SQLModel row (`TodoRow`) mapped to Postgres schema `todos`, table `todo`. `SqlTodoRepository` implements `TodoRepository` using a SQLModel `Session`.
- `features/todos/handlers` — `APIRouter(prefix="/v1/todos", tags=["todos"])` with router-level `Depends(get_current_principal)`. Request schemas: `CreateTodoRequest(title: str, description: str | None)`, `UpdateTodoRequest` (all fields optional). Response schema: `TodoResponse`. Routes per API contract below.
- `features/todos/deps` — The only file that imports both `usecases` and `adapters`. Exposes `Annotated` use-case dependencies.
- `features/todos/__init__` — Exposes `register(app: FastAPI)`.

**Composition (new)**
- `app/main.py` — `create_app()` builds the FastAPI instance: installs middleware (request-id, structlog), calls `shared/http/error_handlers.register(app)`, calls `todos.register(app)`. Lifespan: settings validation, DB engine init, structlog setup.

**Removed**
- Flat `main.py`, `models.py`, `database.py`, `test_main.py`, `Item` model.

### Auth
- Dummy bearer auth: `Authorization: Bearer <username>` → `Principal(id=<username>)`. No password, no signature validation.
- Missing or blank header raises `UnauthorizedError`, mapped to 401 Problem by the shared handler.
- All `/v1/todos` routes require a principal. The router-level dependency enforces this uniformly.

### API contract

| Method | Path | Success | Notes |
|--------|------|---------|-------|
| `POST` | `/v1/todos` | 201 + `Location` header | Body: `CreateTodoRequest` |
| `GET` | `/v1/todos` | 200 `ListEnvelope[TodoResponse]` | `?cursor=&limit=&completed=` |
| `GET` | `/v1/todos/{id}` | 200 `TodoResponse` | 404 if not found or wrong owner |
| `PATCH` | `/v1/todos/{id}` | 200 `TodoResponse` | Partial update; 404 if not found or wrong owner |
| `DELETE` | `/v1/todos/{id}` | 204 | 404 if not found or wrong owner |

### Pagination
- Cursor encodes `(created_at ISO 8601, id)` separated by `|`, base64-encoded. Opaque to clients.
- Default sort: `created_at DESC`, tie-broken by `id DESC`.
- Default `limit=20`, max `limit=100`. Out-of-range values clamped, not rejected.
- `ListEnvelope` includes `items: list[T]` and `next_cursor: str | None` (null when no more pages).

### Persistence
- Postgres schema: `todos`. Table: `todos.todo`.
- ID: `int`, autoincrement, primary key.
- `owner_id`: `str`, not null, indexed.
- `created_at` / `updated_at`: `timestamptz`, set by the adapter on write (not DB default), so the domain controls the value.
- Alembic configured with per-module schema isolation; initial migration creates `todos.todo`.

### Settings
- `DATABASE_URL` read from environment, defaulting to local Postgres.
- Settings validated at startup (fail-fast in lifespan).

## Testing Decisions

**What makes a good test:** Tests assert on observable, external behaviour — HTTP response codes, body shapes, persisted state — not on internal implementation details like which repository method was called or how a query was constructed. Tests must remain valid across refactors as long as the contract is unchanged.

**Unit tests** (`tests/todos/unit/`)
- `shared/http/pagination`: cursor round-trip (encode → decode → same values), last-page returns `next_cursor=None`, `clamp_limit` enforces bounds. Pure functions; no app or DB needed.
- Todos use cases (`CreateTodo`, `ListTodos`, `GetTodo`, `UpdateTodo`, `DeleteTodo`) exercised with `InMemoryTodoRepository`. Cover: happy path, `TodoNotFound` raised on wrong owner or missing ID, owner-scoping (principal A cannot see principal B's todos). No framework involved.

**Integration tests** (`tests/todos/integration/`)
- Real Postgres via testcontainers. Tests spin up a container, run migrations, and exercise the full FastAPI app via `TestClient`.
- Named using EARS convention:
  - `test_when_authenticated_post_todos_shall_return_201_with_location`
  - `test_when_authenticated_get_todos_shall_return_envelope_scoped_to_owner`
  - `test_when_authenticated_get_todo_shall_return_200`
  - `test_when_authenticated_patch_todo_shall_update_fields`
  - `test_when_authenticated_delete_todo_shall_return_204`
  - `test_if_authorization_header_missing_any_todos_route_shall_return_401_problem`
  - `test_if_todo_belongs_to_other_owner_get_todo_shall_return_404_problem`
  - `test_if_request_body_invalid_post_todos_shall_return_422_problem_with_errors`
  - `test_when_paginating_todos_cursor_returns_next_page`
  - `test_when_filtering_by_completed_get_todos_shall_return_only_matching`
- `tests/conftest.py` owns the testcontainers fixture (Postgres container + engine + migration run + session factory).

**Skipped**
- `deps.py` (DI wiring only, no logic).
- Handler schemas (Pydantic-enforced invariants covered by 422 integration test).
- `SqlTodoRepository` in isolation (fully covered transitively by integration tests).
- Trivial passthrough getters.

**Prior art:** No existing integration tests in the repo yet — these will be the first. The patterns above establish the baseline for all future modules.

## Out of Scope

- Real authentication (JWT, OAuth, session tokens, password hashing).
- Multi-list or labelling (todos belong to lists, tags, projects).
- Due dates and priority fields.
- Soft delete / archival.
- Audit log / change history.
- Rate limiting.
- Notifications or webhooks triggered by todo state changes.
- Search (`?q=`) — filter by `completed` is the only supported query parameter.
- Versioning beyond `/v1` (no `/v2` breakage anticipated for this feature yet).
- Frontend or client SDKs.

## Further Notes

- When real auth lands, only `shared/auth/dependencies.py` changes. `Principal`, commands, use cases, handlers, and tests remain untouched — the contract is stable.
- The `owner_id` column uses `str` (matching `Principal.id`) so that any future principal identifier format (UUID, email, sub claim) is compatible without a schema change.
- The in-memory fake shipped with the todos module is immediately reusable by any future module that depends on `features/todos/api.py` (e.g., a notifications module that needs to look up todo titles).
- Import-linter contracts should be added to `pyproject.toml` and run as part of the lint step in CI alongside ruff and mypy.
