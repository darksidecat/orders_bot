import uuid
from datetime import datetime
from typing import List
from uuid import UUID

import attrs
from attrs import validators

from app.domain.common.events.event import Event
from app.domain.common.models.aggregate import Aggregate
from app.domain.common.models.entity import entity
from app.domain.goods import dto
from app.domain.goods.models.goods import Goods
from app.domain.market.models.market import Market
from app.domain.user.models.user import TelegramUser


@entity
class OrderLine:
    id: UUID = attrs.field(validator=validators.instance_of(UUID))
    goods: Goods = attrs.field(validator=validators.instance_of(Goods))
    quantity: int = attrs.field(validator=validators.instance_of(int))


@entity
class Order(Aggregate):
    id: UUID = attrs.field(validator=validators.instance_of(UUID), factory=uuid.uuid4)
    order_lines: List[OrderLine] = attrs.field(factory=list)
    creator_id: int = attrs.field(validator=validators.instance_of(int))
    creator: TelegramUser = attrs.field(validator=validators.instance_of(TelegramUser))
    created_at: datetime = attrs.field(
        validator=validators.instance_of(datetime), factory=datetime.now
    )
    recipient_market: Market = attrs.field(validator=validators.instance_of(Market))
    commentary: str = attrs.field(validator=validators.instance_of(str))

    @classmethod
    def create(cls, creator_id: int, order_lines: List[OrderLine]):
        order = Order(creator_id=creator_id, order_lines=order_lines)
        order.events.append(OrderCreated(dto.Goods.from_orm(order)))

        return order

    def add_order_line(self, order_line: OrderLine):
        self.order_lines.append(order_line)


class OrderCreated(Event):
    def __init__(self, order: dto.Goods):
        self.order = order
