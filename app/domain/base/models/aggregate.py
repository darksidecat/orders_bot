from typing import List

import attrs

from app.domain.base.events.event import Event
from app.domain.base.models.entity import entity


@entity
class Aggregate:
    _events: List[Event] = attrs.field(factory=list, repr=False)

    @property
    def events(self):
        # there is strange bug with attrs and sqlalchemy
        # after loading from db, aggregate._events is not present as attribute,
        # so we need to create it manually
        if not hasattr(self, "_events"):
            self._events = []
        return self._events
