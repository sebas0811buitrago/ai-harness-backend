from features.todos.usecases.commands import DeleteTodoCommand
from features.todos.usecases.ports.todo_repository import TodoRepository


class DeleteTodo:
    def __init__(self, *, repo: TodoRepository) -> None:
        self._repo = repo

    async def __call__(self, cmd: DeleteTodoCommand) -> None:
        await self._repo.delete_for_owner(cmd.todo_id, cmd.principal.id)
