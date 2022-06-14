from typing import List, Type

from app.domain.base.events.event import Event
from app.domain.base.events.observer import Handler, Observer


class EventDispatcher:
    def __init__(self, **kwargs):
        self.domain_events = Observer()
        self.notifications = Observer()
        self.data = kwargs

    async def publish_events(self, events: List[Event]):
        await self.domain_events.notify(events, data=self.data.copy())

    async def publish_notifications(self, events: List[Event]):
        await self.notifications.notify(events, data=self.data.copy())

    def register_domain_event(self, event_type: Type[Event], handler: Handler):
        self.domain_events.register(event_type, handler)

    def register_notify(self, event_type: Type[Event], handler: Handler):
        self.notifications.register(event_type, handler)
