from datetime import datetime, timezone
from typing import Callable

from features.todos.domain.entities import NewTodo, Todo
from features.todos.usecases.commands import CreateTodoCommand
from features.todos.usecases.ports.todo_repository import TodoRepository


class CreateTodo:
    def __init__(
        self,
        *,
        repo: TodoRepository,
        clock: Callable[[], datetime] = lambda: datetime.now(tz=timezone.utc),
    ) -> None:
        self._repo = repo
        self._clock = clock

    async def __call__(self, cmd: CreateTodoCommand) -> Todo:
        now = self._clock()
        new_todo = NewTodo(
            owner_id=cmd.principal.id,
            title=cmd.title,
            description=cmd.description,
            created_at=now,
            updated_at=now,
        )
        return await self._repo.add(new_todo)
