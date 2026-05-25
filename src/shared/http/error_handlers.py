from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from shared.errors.base import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)

_PROBLEM_MEDIA_TYPE = "application/problem+json"
# Base URI for problem type documents (RFC 9457 §3 — type MUST be a URI reference).
# Point this at your API docs once you publish them; "about:blank" is the RFC-sanctioned
# fallback meaning "no additional semantics beyond the HTTP status code."
_PROBLEMS_BASE_URI = "/problems"


def _type_uri(slug: str) -> str:
    return f"{_PROBLEMS_BASE_URI}/{slug}"


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
        "type": _type_uri(type_slug),
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

    @app.exception_handler(StarletteHTTPException)
    async def _http_exception(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        _STATUS_MAP: dict[int, tuple[str, str]] = {
            400: ("bad-request", "Bad Request"),
            401: ("unauthorized", "Unauthorized"),
            403: ("forbidden", "Forbidden"),
            404: ("not-found", "Not Found"),
            405: ("method-not-allowed", "Method Not Allowed"),
            409: ("conflict", "Conflict"),
        }
        slug, title = _STATUS_MAP.get(exc.status_code, ("error", "Error"))
        return _problem(request, exc, exc.status_code, slug, title, detail=exc.detail)

    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception) -> JSONResponse:
        return _problem(request, exc, 500, "internal-server-error", "Internal Server Error", detail="An unexpected error occurred.")
