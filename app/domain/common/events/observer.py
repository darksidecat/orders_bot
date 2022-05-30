import functools
from typing import Any, Awaitable, Callable, Dict, List, Type

from app.domain.common.events.base import MiddlewareType, NextMiddlewareType
from app.domain.common.events.event import Event

Handler = Callable[[Event, Dict[str, Any]], Awaitable[Any]]


class Observer:
    def __init__(self):
        self.handlers: Dict[Type[Event], List[Handler]] = {}
        self.middlewares: List[MiddlewareType] = []

    async def notify(self, events: List[Event], data: Dict[str, Any]):
        for event in events:
            handlers = self.handlers.get(type(event), [])
            for handler in handlers:
                wrapped_handler = self._wrap_middleware(self.middlewares, handler)
                await wrapped_handler(event, data)

    def register(self, event_type: Type[Event], handler: Handler):
        handlers = self.handlers.setdefault(event_type, [])
        handlers.append(handler)

    @classmethod
    def _wrap_middleware(
        cls, middlewares: List[MiddlewareType], handler: Handler
    ) -> NextMiddlewareType:
        @functools.wraps(handler)
        def mapper(event: Event, data: Dict[str, Any]) -> Any:
            return handler(event, data)

        middleware = mapper
        for m in reversed(middlewares):
            middleware = functools.partial(m, middleware)
        return middleware

    def middleware(self, middleware: MiddlewareType):
        self.middlewares.append(middleware)
        return middleware
