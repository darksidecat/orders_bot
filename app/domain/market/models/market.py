from __future__ import annotations

import uuid
from uuid import UUID

import attrs
from attrs import validators

from app.domain.base.events.event import Event
from app.domain.base.models.aggregate import Aggregate
from app.domain.base.models.entity import entity
from app.domain.market import dto


@entity
class Market(Aggregate):
    id: UUID = attrs.field(validator=validators.instance_of(UUID), factory=uuid.uuid4)
    name: str = attrs.field(validator=validators.instance_of(str))
    is_active: bool = attrs.field(validator=validators.instance_of(bool), default=True)

    @classmethod
    def create(cls, name: str) -> Market:
        market = Market(name=name)
        market.events.append(MarketCreated(dto.Market.from_orm(market)))

        return market

    def __eq__(self, other):
        return self.id == other.id


class MarketCreated(Event):
    def __init__(self, market: dto.Market):
        self.market = market
