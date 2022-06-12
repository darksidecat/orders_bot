from typing import List

import attrs

from app.domain.common.events.event import Event
from app.domain.common.models.entity import entity


@entity
class Aggregate:
    _events: List[Event] = attrs.field(factory=list, repr=False)

    @property
    def events(self):
        return self._events
