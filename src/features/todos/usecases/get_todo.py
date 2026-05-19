from features.todos.domain.entities import Todo
from features.todos.usecases.commands import GetTodoCommand
from features.todos.usecases.ports.todo_repository import TodoRepository


class GetTodo:
    def __init__(self, *, repo: TodoRepository) -> None:
        self._repo = repo

    async def __call__(self, cmd: GetTodoCommand) -> Todo:
        return await self._repo.get_for_owner(cmd.todo_id, cmd.principal.id)
