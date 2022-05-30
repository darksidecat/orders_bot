from typing import List

from attrs import Factory, field

from app.domain.common.events.event import Event
from app.domain.common.models.entity import entity


@entity
class Aggregate:
    events: List[Event] = field(default=Factory(list))
