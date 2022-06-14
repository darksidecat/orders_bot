from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Awaitable, Callable, Dict

from app.domain.base.events.event import Event


class BaseMiddleware(ABC):
    @abstractmethod
    async def __call__(
        self,
        handler: Callable[[Event, Dict[str, Any]], Awaitable[Any]],
        event: Event,
        data: Dict[str, Any],
    ) -> Any:
        """
        Execute middleware
        :param handler: Wrapped handler in middlewares chain
        :param event: Incoming event
        :param data: Contextual data
        :return: :class:`Any`
        """
        pass
