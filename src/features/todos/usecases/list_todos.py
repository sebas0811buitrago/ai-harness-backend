from features.todos.domain.entities import Todo
from features.todos.usecases.commands import ListTodosCommand
from features.todos.usecases.ports.todo_repository import TodoRepository


class ListTodos:
    def __init__(self, *, repo: TodoRepository) -> None:
        self._repo = repo

    async def __call__(self, cmd: ListTodosCommand) -> tuple[list[Todo], str | None]:
        return await self._repo.list_for_owner(
            owner_id=cmd.principal.id,
            completed=cmd.completed,
            cursor=cmd.cursor,
            limit=cmd.limit,
        )
