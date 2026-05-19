from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from shared.errors.base import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)

_PROBLEM_MEDIA_TYPE = "application/problem+json"


def _problem(
    request: Request,
    exc: Exception,
    status: int,
    type_slug: str,
    title: str,
    detail: str | None = None,
    extra: dict | None = None,
) -> JSONResponse:
    body: dict = {
        "type": type_slug,
        "title": title,
        "status": status,
        "detail": detail if detail is not None else str(exc),
        "instance": str(request.url.path),
    }
    if extra:
        body.update(extra)
    return JSONResponse(status_code=status, content=body, media_type=_PROBLEM_MEDIA_TYPE)


def register(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    async def _not_found(request: Request, exc: NotFoundError) -> JSONResponse:
        return _problem(request, exc, 404, "not-found", "Not Found")

    @app.exception_handler(ConflictError)
    async def _conflict(request: Request, exc: ConflictError) -> JSONResponse:
        return _problem(request, exc, 409, "conflict", "Conflict")

    @app.exception_handler(ValidationError)
    async def _validation(request: Request, exc: ValidationError) -> JSONResponse:
        return _problem(request, exc, 422, "validation-error", "Validation Error")

    @app.exception_handler(UnauthorizedError)
    async def _unauthorized(request: Request, exc: UnauthorizedError) -> JSONResponse:
        return _problem(request, exc, 401, "unauthorized", "Unauthorized")

    @app.exception_handler(ForbiddenError)
    async def _forbidden(request: Request, exc: ForbiddenError) -> JSONResponse:
        return _problem(request, exc, 403, "forbidden", "Forbidden")

    @app.exception_handler(RequestValidationError)
    async def _request_validation(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors = [
            {"field": ".".join(str(loc) for loc in e["loc"]), "message": e["msg"]}
            for e in exc.errors()
        ]
        return _problem(
            request,
            exc,
            422,
            "validation-error",
            "Validation Error",
            detail="Request validation failed.",
            extra={"errors": errors},
        )
