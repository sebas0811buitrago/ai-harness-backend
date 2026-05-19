from typing import Any

from features.todos.domain.entities import NewTodo, Todo
from features.todos.domain.errors import TodoNotFound
from shared.http.pagination import decode_cursor, encode_cursor


class InMemoryTodoRepository:
    def __init__(self) -> None:
        self._todos: dict[int, Todo] = {}
        self._next_id: int = 1

    @classmethod
    def with_existing(cls, *todos: Todo) -> "InMemoryTodoRepository":
        repo = cls()
        for todo in todos:
            repo._todos[todo.id] = todo
            if todo.id >= repo._next_id:
                repo._next_id = todo.id + 1
        return repo

    async def add(self, new_todo: NewTodo) -> Todo:
        todo = Todo(id=self._next_id, **new_todo.model_dump())
        self._todos[self._next_id] = todo
        self._next_id += 1
        return todo

    async def get_for_owner(self, id: int, owner_id: str) -> Todo:
        todo = self._todos.get(id)
        if todo is None or todo.owner_id != owner_id:
            raise TodoNotFound(f"Todo {id} not found")
        return todo

    async def list_for_owner(
        self,
        owner_id: str,
        completed: bool | None,
        cursor: str | None,
        limit: int,
    ) -> tuple[list[Todo], str | None]:
        items = [t for t in self._todos.values() if t.owner_id == owner_id]
        if completed is not None:
            items = [t for t in items if t.completed == completed]

        items.sort(key=lambda t: (t.created_at, t.id), reverse=True)

        if cursor:
            cursor_dt, cursor_id = decode_cursor(cursor)
            items = [
                t
                for t in items
                if t.created_at < cursor_dt
                or (t.created_at == cursor_dt and t.id < cursor_id)
            ]

        page = items[:limit]
        next_cursor: str | None = None
        if len(items) > limit:
            last = page[-1]
            next_cursor = encode_cursor(last.created_at, last.id)

        return page, next_cursor

    async def update(self, id: int, owner_id: str, patch: dict[str, Any]) -> Todo:
        todo = self._todos.get(id)
        if todo is None or todo.owner_id != owner_id:
            raise TodoNotFound(f"Todo {id} not found")
        updated = todo.model_copy(update=patch)
        self._todos[id] = updated
        return updated

    async def delete_for_owner(self, id: int, owner_id: str) -> None:
        todo = self._todos.get(id)
        if todo is None or todo.owner_id != owner_id:
            raise TodoNotFound(f"Todo {id} not found")
        del self._todos[id]
