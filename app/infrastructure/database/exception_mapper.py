from functools import wraps
from typing import Any, Callable

from sqlalchemy.exc import IntegrityError

from app.domain.common.exceptions import repo


def exception_mapper(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    async def wrapped(*args: Any, **kwargs: Any):
        try:
            return await func(*args, **kwargs)
        except IntegrityError as err:
            raise repo.UniqueViolationError from err

    return wrapped
