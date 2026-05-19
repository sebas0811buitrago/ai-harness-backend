from pydantic import BaseModel


class Principal(BaseModel, frozen=True):
    id: str
