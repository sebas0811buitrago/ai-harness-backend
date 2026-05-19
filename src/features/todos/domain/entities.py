from datetime import datetime

from pydantic import BaseModel


class Todo(BaseModel, frozen=True, extra="forbid"):
    id: int
    owner_id: str
    title: str
    description: str | None
    completed: bool
    created_at: datetime
    updated_at: datetime


class NewTodo(BaseModel, frozen=True, extra="forbid"):
    """Data required to persist a new todo; the adapter assigns the id."""

    owner_id: str
    title: str
    description: str | None = None
    completed: bool = False
    created_at: datetime
    updated_at: datetime
