from fastapi import Header

from shared.auth.models import Principal
from shared.errors.base import UnauthorizedError


async def get_current_principal(
    authorization: str | None = Header(default=None),
) -> Principal:
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedError("Missing or invalid Authorization header")
    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise UnauthorizedError("Missing or invalid Authorization header")
    return Principal(id=token)
