class AppError(Exception):
    """Base class for all domain errors."""


class NotFoundError(AppError):
    """Resource does not exist or is not accessible to the caller."""


class ConflictError(AppError):
    """Operation would create a duplicate or conflicting state."""


class ValidationError(AppError):
    """Input violates a domain business rule."""


class UnauthorizedError(AppError):
    """Request lacks valid authentication credentials."""


class ForbiddenError(AppError):
    """Authenticated caller lacks permission for this action."""
