from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel

from features.todos.deps import (
    CreateTodoDep,
    DeleteTodoDep,
    GetTodoDep,
    ListTodosDep,
    UpdateTodoDep,
)
from features.todos.domain.entities import Todo
from features.todos.usecases.commands import (
    CreateTodoCommand,
    DeleteTodoCommand,
    GetTodoCommand,
    ListTodosCommand,
    UpdateTodoCommand,
)
from shared.auth.dependencies import get_current_principal
from shared.auth.models import Principal
from shared.http.pagination import ListEnvelope

router = APIRouter(
    prefix="/v1/todos",
    tags=["todos"],
    dependencies=[Depends(get_current_principal)],
)

PrincipalDep = Annotated[Principal, Depends(get_current_principal)]


class CreateTodoRequest(BaseModel):
    title: str
    description: str | None = None


class UpdateTodoRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None


class TodoResponse(BaseModel):
    id: int
    owner_id: str
    title: str
    description: str | None
    completed: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, todo: Todo) -> "TodoResponse":
        return cls(**todo.model_dump())


@router.post("", status_code=201)
async def create_todo(
    body: CreateTodoRequest,
    principal: PrincipalDep,
    use_case: CreateTodoDep,
    response: Response,
) -> TodoResponse:
    todo = await use_case(
        CreateTodoCommand(
            principal=principal,
            title=body.title,
            description=body.description,
        )
    )
    response.headers["Location"] = f"/v1/todos/{todo.id}"
    return TodoResponse.from_domain(todo)


@router.get("", status_code=200)
async def list_todos(
    principal: PrincipalDep,
    use_case: ListTodosDep,
    cursor: str | None = None,
    limit: int = 20,
    completed: bool | None = None,
) -> ListEnvelope[TodoResponse]:
    items, next_cursor = await use_case(
        ListTodosCommand(
            principal=principal,
            cursor=cursor,
            limit=limit,
            completed=completed,
        )
    )
    return ListEnvelope(
        items=[TodoResponse.from_domain(t) for t in items],
        next_cursor=next_cursor,
    )


@router.get("/{todo_id}", status_code=200)
async def get_todo(
    todo_id: int,
    principal: PrincipalDep,
    use_case: GetTodoDep,
) -> TodoResponse:
    todo = await use_case(GetTodoCommand(principal=principal, todo_id=todo_id))
    return TodoResponse.from_domain(todo)


@router.patch("/{todo_id}", status_code=200)
async def update_todo(
    todo_id: int,
    body: UpdateTodoRequest,
    principal: PrincipalDep,
    use_case: UpdateTodoDep,
) -> TodoResponse:
    todo = await use_case(
        UpdateTodoCommand(
            principal=principal,
            todo_id=todo_id,
            title=body.title,
            description=body.description,
            completed=body.completed,
        )
    )
    return TodoResponse.from_domain(todo)


@router.delete("/{todo_id}", status_code=204)
async def delete_todo(
    todo_id: int,
    principal: PrincipalDep,
    use_case: DeleteTodoDep,
) -> None:
    await use_case(DeleteTodoCommand(principal=principal, todo_id=todo_id))
