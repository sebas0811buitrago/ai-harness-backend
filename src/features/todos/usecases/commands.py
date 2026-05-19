from pydantic import BaseModel

from shared.auth.models import Principal


class CreateTodoCommand(BaseModel, frozen=True):
    principal: Principal
    title: str
    description: str | None = None


class GetTodoCommand(BaseModel, frozen=True):
    principal: Principal
    todo_id: int


class ListTodosCommand(BaseModel, frozen=True):
    principal: Principal
    cursor: str | None = None
    limit: int = 20
    completed: bool | None = None


class UpdateTodoCommand(BaseModel, frozen=True):
    principal: Principal
    todo_id: int
    title: str | None = None
    description: str | None = None
    completed: bool | None = None


class DeleteTodoCommand(BaseModel, frozen=True):
    principal: Principal
    todo_id: int
