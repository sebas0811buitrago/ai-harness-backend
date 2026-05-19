# Tests

## Picking a tier

The project mandates two tiers and no mocked-DB middle tier — see [`conventions.md` — Testing](../../../docs/architecture/conventions.md#testing).

**Test behavior at the tier the behavior lives in.**

| Behavior under test                                    | Tier         | Where                          |
|---                                                     |---           |---                             |
| Use case logic, command validation, domain errors      | Unit         | `tests/<module>/unit/`         |
| Complex domain rules / invariants                      | Unit         | `tests/<module>/unit/`         |
| HTTP contract (status, body shape, headers)            | Integration  | `tests/<module>/integration/`  |
| Authorization, principal handling                      | Integration  | `tests/<module>/integration/`  |
| Persistence, adapter ↔ port symmetry                   | Integration  | `tests/<module>/integration/`  |
| Cross-module composition via another module's `api.py` | Integration  | `tests/<module>/integration/`  |

`conventions.md` already directs you to skip trivial getters and Pydantic-enforced invariants — honor it.

## Naming

- **Unit tests** — name reflects the capability under test (use-case-shaped). Examples:
  - `test_create_invoice_rejects_duplicate_external_id`
  - `test_settle_invoice_marks_status_paid_when_amount_matches`

- **Integration tests** — EARS-style sentence per [`conventions.md` — Testing](../../../docs/architecture/conventions.md#testing). Examples:
  - `test_when_principal_is_admin_post_invoices_shall_return_201_with_location`
  - `test_if_external_id_duplicates_post_invoices_shall_return_409`

The shape "**when** `<event>`, **the** `<endpoint>` **shall** `<response>`" (event-driven) and "**if** `<unwanted>`, **then** `<endpoint>` **shall** `<response>`" (unwanted-behavior) are the two EARS forms you'll use most.

## Unit test example — use case + fake

```python
import pytest

from features.billing.domain.errors import DuplicateExternalIdError
from features.billing.usecases.commands import CreateInvoiceCommand
from features.billing.usecases.create_invoice import CreateInvoice
from features.billing.usecases.ports._fakes import FakeInvoiceRepository


@pytest.mark.asyncio
async def test_create_invoice_rejects_duplicate_external_id() -> None:
    repo = FakeInvoiceRepository.with_existing(external_id="EXT-1")
    use_case = CreateInvoice(repository=repo)

    with pytest.raises(DuplicateExternalIdError):
        await use_case(CreateInvoiceCommand(external_id="EXT-1", amount_cents=1_000))
```

The test asserts on the raised domain error. It does not inspect `repo`'s internal storage.

## Integration test example — AsyncClient + testcontainers

```python
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_when_principal_is_admin_post_invoices_shall_return_201_with_location(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/v1/invoices",
        json={"external_id": "EXT-1", "amount_cents": 1_000},
    )

    assert response.status_code == 201
    assert response.headers["Location"].startswith("/v1/invoices/")
```

The DB write is verified by reading it back through the same HTTP surface in a follow-up test — never by querying Postgres directly.

## Good test / bad test

**Good:**

- Asserts on the use case's return value or raised domain error.
- Reads state via the same public path another caller would use.
- Survives an adapter rewrite (Postgres → DynamoDB) without modification.
- Test name describes a capability.

**Bad:**

- Reaches into `FakeRepository._items` to assert presence.
- Asserts `repo.save.called_once_with(...)` — `AsyncMock` is banned, see [fakes.md](fakes.md).
- Queries the test database with raw SQL instead of going through the API.
- Renaming a private helper inside the use case breaks the test.
