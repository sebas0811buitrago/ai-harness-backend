from datetime import datetime, timezone

from features.todos.domain.entities import Todo
from features.todos.usecases.commands import ListTodosCommand
from features.todos.usecases.list_todos import ListTodos
from features.todos.usecases.ports._fakes import InMemoryTodoRepository
from shared.auth.models import Principal

_NOW = datetime(2024, 1, 1, tzinfo=timezone.utc)


def _make_todo(id: int, owner_id: str, completed: bool = False) -> Todo:
    return Todo(
        id=id,
        owner_id=owner_id,
        title=f"Todo {id}",
        description=None,
        completed=completed,
        created_at=_NOW,
        updated_at=_NOW,
    )


async def test_list_todos_returns_only_owner_todos() -> None:
    alice_todo = _make_todo(id=1, owner_id="alice")
    bob_todo = _make_todo(id=2, owner_id="bob")
    repo = InMemoryTodoRepository.with_existing(alice_todo, bob_todo)
    use_case = ListTodos(repo=repo)

    items, _ = await use_case(ListTodosCommand(principal=Principal(id="alice")))

    assert items == [alice_todo]


async def test_list_todos_filters_by_completed() -> None:
    open_todo = _make_todo(id=1, owner_id="alice", completed=False)
    done_todo = _make_todo(id=2, owner_id="alice", completed=True)
    repo = InMemoryTodoRepository.with_existing(open_todo, done_todo)
    use_case = ListTodos(repo=repo)

    items, _ = await use_case(
        ListTodosCommand(principal=Principal(id="alice"), completed=True)
    )

    assert items == [done_todo]


async def test_list_todos_returns_next_cursor_when_more_pages_exist() -> None:
    todos = [_make_todo(id=i, owner_id="alice") for i in range(1, 4)]
    repo = InMemoryTodoRepository.with_existing(*todos)
    use_case = ListTodos(repo=repo)

    _, next_cursor = await use_case(
        ListTodosCommand(principal=Principal(id="alice"), limit=2)
    )

    assert next_cursor is not None
