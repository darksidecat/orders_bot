from __future__ import annotations

import uuid
from uuid import UUID

import attrs
from attrs import validators

from app.domain.common.events.event import Event
from app.domain.common.models.aggregate import Aggregate
from app.domain.common.models.entity import entity
from app.domain.market import dto


@entity
class Market(Aggregate):
    id: UUID = attrs.field(validator=validators.instance_of(UUID), factory=uuid.uuid4)
    name: str = attrs.field(validator=validators.instance_of(str))

    @classmethod
    def create(cls, name: str) -> Market:
        market = Market(name=name)
        market.events.append(MarketCreated(dto.Market.from_orm(market)))

        return market


class MarketCreated(Event):
    def __init__(self, market: dto.Market):
        self.market = market
