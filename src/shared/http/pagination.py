import base64
from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ListEnvelope(BaseModel, Generic[T]):
    items: list[T]
    next_cursor: str | None = None


def encode_cursor(created_at: datetime, id: int) -> str:
    raw = f"{created_at.isoformat()}|{id}"
    return base64.urlsafe_b64encode(raw.encode()).decode()


def decode_cursor(cursor: str) -> tuple[datetime, int]:
    raw = base64.urlsafe_b64decode(cursor.encode()).decode()
    created_at_str, id_str = raw.split("|", 1)
    return datetime.fromisoformat(created_at_str), int(id_str)


def clamp_limit(limit: int, default: int = 20, max_limit: int = 100) -> int:
    if limit <= 0:
        return default
    return min(limit, max_limit)
