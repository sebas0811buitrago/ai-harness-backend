from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from features.todos.adapters.db.models import TodoRow
from features.todos.domain.entities import NewTodo, Todo
from features.todos.domain.errors import TodoNotFound
from shared.http.pagination import decode_cursor, encode_cursor


class SqlTodoRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_domain(self, row: TodoRow) -> Todo:
        return Todo(
            id=row.id,  # type: ignore[arg-type]
            owner_id=row.owner_id,
            title=row.title,
            description=row.description,
            completed=row.completed,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    async def add(self, new_todo: NewTodo) -> Todo:
        row = TodoRow(
            owner_id=new_todo.owner_id,
            title=new_todo.title,
            description=new_todo.description,
            completed=new_todo.completed,
            created_at=new_todo.created_at,
            updated_at=new_todo.updated_at,
        )
        self._session.add(row)
        await self._session.flush()
        await self._session.refresh(row)
        return self._to_domain(row)

    async def get_for_owner(self, id: int, owner_id: str) -> Todo:
        stmt = select(TodoRow).where(TodoRow.id == id, TodoRow.owner_id == owner_id)
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            raise TodoNotFound(f"Todo {id} not found")
        return self._to_domain(row)

    async def list_for_owner(
        self,
        owner_id: str,
        completed: bool | None,
        cursor: str | None,
        limit: int,
    ) -> tuple[list[Todo], str | None]:
        stmt = select(TodoRow).where(TodoRow.owner_id == owner_id)
        if completed is not None:
            stmt = stmt.where(TodoRow.completed == completed)
        if cursor:
            cursor_dt, cursor_id = decode_cursor(cursor)
            stmt = stmt.where(
                (TodoRow.created_at < cursor_dt)
                | ((TodoRow.created_at == cursor_dt) & (TodoRow.id < cursor_id))
            )
        stmt = stmt.order_by(TodoRow.created_at.desc(), TodoRow.id.desc())  # type: ignore[union-attr]
        stmt = stmt.limit(limit + 1)

        result = await self._session.execute(stmt)
        rows = list(result.scalars())

        next_cursor: str | None = None
        if len(rows) > limit:
            rows = rows[:limit]
            last = rows[-1]
            next_cursor = encode_cursor(last.created_at, last.id)  # type: ignore[arg-type]

        return [self._to_domain(r) for r in rows], next_cursor

    async def update(self, id: int, owner_id: str, patch: dict[str, Any]) -> Todo:
        stmt = select(TodoRow).where(TodoRow.id == id, TodoRow.owner_id == owner_id)
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            raise TodoNotFound(f"Todo {id} not found")
        for key, value in patch.items():
            setattr(row, key, value)
        await self._session.flush()
        await self._session.refresh(row)
        return self._to_domain(row)

    async def delete_for_owner(self, id: int, owner_id: str) -> None:
        stmt = select(TodoRow).where(TodoRow.id == id, TodoRow.owner_id == owner_id)
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            raise TodoNotFound(f"Todo {id} not found")
        await self._session.delete(row)
        await self._session.flush()
