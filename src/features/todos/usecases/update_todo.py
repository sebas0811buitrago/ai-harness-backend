from features.todos.domain.entities import Todo
from features.todos.usecases.commands import UpdateTodoCommand
from features.todos.usecases.ports.todo_repository import TodoRepository


class UpdateTodo:
    def __init__(self, *, repo: TodoRepository) -> None:
        self._repo = repo

    async def __call__(self, cmd: UpdateTodoCommand) -> Todo:
        patch = {
            k: v
            for k, v in {
                "title": cmd.title,
                "description": cmd.description,
                "completed": cmd.completed,
            }.items()
            if v is not None
        }
        return await self._repo.update(cmd.todo_id, cmd.principal.id, patch)
