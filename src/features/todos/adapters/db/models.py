from datetime import datetime

import sqlalchemy as sa
from sqlmodel import Field, SQLModel


class TodoRow(SQLModel, table=True):
    __tablename__ = "todo"
    __table_args__ = (
        sa.Index("ix_todos_todo_owner_id", "owner_id"),
        {"schema": "todos"},
    )

    id: int | None = Field(default=None, primary_key=True)
    owner_id: str = Field(nullable=False)
    title: str = Field(nullable=False)
    description: str | None = Field(default=None)
    completed: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(nullable=False, sa_type=sa.DateTime(timezone=True))
    updated_at: datetime = Field(nullable=False, sa_type=sa.DateTime(timezone=True))
