from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from pydantic import BaseModel
from sqlmodel import Session

from database import get_session, init_db
from models import Item, ItemCreate, ItemRead


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

SessionDep = Annotated[Session, Depends(get_session)]


class Message(BaseModel):
    message: str


@app.get("/", response_model=Message)
def read_root() -> Message:
    return Message(message="Hello, World!")


@app.post("/items", response_model=ItemRead)
def create_item(item: ItemCreate, session: SessionDep) -> Item:
    db_item = Item.model_validate(item)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item
