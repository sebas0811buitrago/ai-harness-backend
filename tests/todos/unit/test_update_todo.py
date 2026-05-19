from datetime import datetime, timezone

import pytest

from features.todos.domain.entities import Todo
from features.todos.domain.errors import TodoNotFound
from features.todos.usecases.commands import UpdateTodoCommand
from features.todos.usecases.ports._fakes import InMemoryTodoRepository
from features.todos.usecases.update_todo import UpdateTodo
from shared.auth.models import Principal

_NOW = datetime(2024, 1, 1, tzinfo=timezone.utc)


def _make_todo(id: int, owner_id: str) -> Todo:
    return Todo(
        id=id,
        owner_id=owner_id,
        title="Original title",
        description=None,
        completed=False,
        created_at=_NOW,
        updated_at=_NOW,
    )


async def test_update_todo_applies_partial_patch() -> None:
    todo = _make_todo(id=1, owner_id="alice")
    repo = InMemoryTodoRepository.with_existing(todo)
    use_case = UpdateTodo(repo=repo)

    result = await use_case(
        UpdateTodoCommand(
            principal=Principal(id="alice"),
            todo_id=1,
            title="New title",
            completed=True,
        )
    )

    assert result.title == "New title"
    assert result.completed is True
    assert result.description is None


async def test_update_todo_raises_not_found_for_missing() -> None:
    repo = InMemoryTodoRepository()
    use_case = UpdateTodo(repo=repo)

    with pytest.raises(TodoNotFound):
        await use_case(
            UpdateTodoCommand(principal=Principal(id="alice"), todo_id=99, title="X")
        )


async def test_update_todo_raises_not_found_for_other_owners_todo() -> None:
    todo = _make_todo(id=1, owner_id="bob")
    repo = InMemoryTodoRepository.with_existing(todo)
    use_case = UpdateTodo(repo=repo)

    with pytest.raises(TodoNotFound):
        await use_case(
            UpdateTodoCommand(principal=Principal(id="alice"), todo_id=1, title="X")
        )
