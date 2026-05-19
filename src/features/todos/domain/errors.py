from shared.errors.base import NotFoundError


class TodoNotFound(NotFoundError):
    """Todo does not exist or belongs to a different owner."""
