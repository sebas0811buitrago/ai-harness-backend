from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from features.todos.adapters.db.repository import SqlTodoRepository
from features.todos.usecases.create_todo import CreateTodo
from features.todos.usecases.delete_todo import DeleteTodo
from features.todos.usecases.get_todo import GetTodo
from features.todos.usecases.list_todos import ListTodos
from features.todos.usecases.update_todo import UpdateTodo


async def _get_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    async with request.app.state.session_factory() as session:
        async with session.begin():
            yield session


_SessionDep = Annotated[AsyncSession, Depends(_get_session)]


def _make_repo(session: _SessionDep) -> SqlTodoRepository:
    return SqlTodoRepository(session)


_RepoDep = Annotated[SqlTodoRepository, Depends(_make_repo)]


def get_create_todo(repo: _RepoDep) -> CreateTodo:
    return CreateTodo(repo=repo)


def get_get_todo(repo: _RepoDep) -> GetTodo:
    return GetTodo(repo=repo)


def get_list_todos(repo: _RepoDep) -> ListTodos:
    return ListTodos(repo=repo)


def get_update_todo(repo: _RepoDep) -> UpdateTodo:
    return UpdateTodo(repo=repo)


def get_delete_todo(repo: _RepoDep) -> DeleteTodo:
    return DeleteTodo(repo=repo)


CreateTodoDep = Annotated[CreateTodo, Depends(get_create_todo)]
GetTodoDep = Annotated[GetTodo, Depends(get_get_todo)]
ListTodosDep = Annotated[ListTodos, Depends(get_list_todos)]
UpdateTodoDep = Annotated[UpdateTodo, Depends(get_update_todo)]
DeleteTodoDep = Annotated[DeleteTodo, Depends(get_delete_todo)]
