import pytest

from features.todos.domain.entities import Todo
from features.todos.usecases.commands import CreateTodoCommand
from features.todos.usecases.create_todo import CreateTodo
from features.todos.usecases.ports._fakes import InMemoryTodoRepository
from shared.auth.models import Principal


@pytest.fixture
def principal() -> Principal:
    return Principal(id="alice")


@pytest.fixture
def repo() -> InMemoryTodoRepository:
    return InMemoryTodoRepository()


async def test_create_todo_sets_owner_to_principal(
    repo: InMemoryTodoRepository, principal: Principal
) -> None:
    use_case = CreateTodo(repo=repo)

    result = await use_case(CreateTodoCommand(principal=principal, title="Buy milk"))

    assert result.owner_id == principal.id


async def test_create_todo_returns_todo_with_given_title(
    repo: InMemoryTodoRepository, principal: Principal
) -> None:
    use_case = CreateTodo(repo=repo)

    result = await use_case(CreateTodoCommand(principal=principal, title="Buy milk"))

    assert result.title == "Buy milk"


async def test_create_todo_returns_todo_with_description(
    repo: InMemoryTodoRepository, principal: Principal
) -> None:
    use_case = CreateTodo(repo=repo)

    result = await use_case(
        CreateTodoCommand(principal=principal, title="Buy milk", description="2% fat")
    )

    assert isinstance(result, Todo)
    assert result.description == "2% fat"
