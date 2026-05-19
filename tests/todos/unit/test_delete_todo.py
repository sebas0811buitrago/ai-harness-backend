from datetime import datetime, timezone

import pytest

from features.todos.domain.entities import Todo
from features.todos.domain.errors import TodoNotFound
from features.todos.usecases.commands import DeleteTodoCommand, GetTodoCommand
from features.todos.usecases.delete_todo import DeleteTodo
from features.todos.usecases.get_todo import GetTodo
from features.todos.usecases.ports._fakes import InMemoryTodoRepository
from shared.auth.models import Principal

_NOW = datetime(2024, 1, 1, tzinfo=timezone.utc)


def _make_todo(id: int, owner_id: str) -> Todo:
    return Todo(
        id=id,
        owner_id=owner_id,
        title="Sample",
        description=None,
        completed=False,
        created_at=_NOW,
        updated_at=_NOW,
    )


async def test_delete_todo_removes_todo_via_get() -> None:
    todo = _make_todo(id=1, owner_id="alice")
    repo = InMemoryTodoRepository.with_existing(todo)
    delete = DeleteTodo(repo=repo)
    get = GetTodo(repo=repo)

    await delete(DeleteTodoCommand(principal=Principal(id="alice"), todo_id=1))

    with pytest.raises(TodoNotFound):
        await get(GetTodoCommand(principal=Principal(id="alice"), todo_id=1))


async def test_delete_todo_raises_not_found_for_missing() -> None:
    repo = InMemoryTodoRepository()
    use_case = DeleteTodo(repo=repo)

    with pytest.raises(TodoNotFound):
        await use_case(DeleteTodoCommand(principal=Principal(id="alice"), todo_id=99))


async def test_delete_todo_raises_not_found_for_other_owners_todo() -> None:
    todo = _make_todo(id=1, owner_id="bob")
    repo = InMemoryTodoRepository.with_existing(todo)
    use_case = DeleteTodo(repo=repo)

    with pytest.raises(TodoNotFound):
        await use_case(DeleteTodoCommand(principal=Principal(id="alice"), todo_id=1))
