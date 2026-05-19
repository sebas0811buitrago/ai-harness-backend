from typing import Any, Protocol

from features.todos.domain.entities import NewTodo, Todo


class TodoRepository(Protocol):
    async def add(self, new_todo: NewTodo) -> Todo: ...

    async def get_for_owner(self, id: int, owner_id: str) -> Todo:
        """Raises TodoNotFound if id is missing or belongs to a different owner."""
        ...

    async def list_for_owner(
        self,
        owner_id: str,
        completed: bool | None,
        cursor: str | None,
        limit: int,
    ) -> tuple[list[Todo], str | None]: ...

    async def update(self, id: int, owner_id: str, patch: dict[str, Any]) -> Todo:
        """Raises TodoNotFound if id is missing or belongs to a different owner."""
        ...

    async def delete_for_owner(self, id: int, owner_id: str) -> None:
        """Raises TodoNotFound if id is missing or belongs to a different owner."""
        ...
