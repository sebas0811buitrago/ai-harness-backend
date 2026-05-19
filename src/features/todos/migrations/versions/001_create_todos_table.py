"""create todos.todo table

Revision ID: 001
Revises:
Create Date: 2026-05-18 00:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS todos")
    op.create_table(
        "todo",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("owner_id", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("completed", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema="todos",
    )
    op.create_index("ix_todos_todo_owner_id", "todo", ["owner_id"], schema="todos")


def downgrade() -> None:
    op.drop_index("ix_todos_todo_owner_id", table_name="todo", schema="todos")
    op.drop_table("todo", schema="todos")
    op.execute("DROP SCHEMA IF EXISTS todos")
