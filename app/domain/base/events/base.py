from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, Union

from app.domain.base.events.event import Event
from app.domain.base.events.middleware import BaseMiddleware

NextMiddlewareType = Callable[[Event, Dict[str, Any]], Awaitable[Any]]
MiddlewareType = Union[
    BaseMiddleware,
    Callable[[NextMiddlewareType, Event, Dict[str, Any]], Awaitable[Any]],
]
