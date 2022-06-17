import uuid
from datetime import datetime
from typing import List
from uuid import UUID

import attrs
from attrs import validators

from app.domain.base.events.event import Event
from app.domain.base.models.aggregate import Aggregate
from app.domain.base.models.entity import entity
from app.domain.order import dto
from app.domain.order.dto import User
from app.domain.order.exceptions.order import OrderAlreadyConfirmed
from app.domain.order.value_objects.confirmed_status import ConfirmedStatus
from app.domain.order.models.goods import Goods
from app.domain.order.models.market import Market
from app.domain.order.models.user import TelegramUser


@entity
class OrderLine:
    id: UUID = attrs.field(validator=validators.instance_of(UUID), factory=uuid.uuid4)
    goods: Goods = attrs.field(validator=validators.instance_of(Goods))
    quantity: int = attrs.field(validator=validators.instance_of(int))


@entity
class OrderMessage:
    id: UUID = attrs.field(validator=validators.instance_of(UUID), factory=uuid.uuid4)
    message_id: int = attrs.field(validator=validators.instance_of(int))
    chat_id: int = attrs.field(validator=validators.instance_of(int))


@entity
class Order(Aggregate):
    id: UUID = attrs.field(validator=validators.instance_of(UUID), factory=uuid.uuid4)
    order_lines: List[OrderLine] = attrs.field(factory=list)
    creator: TelegramUser = attrs.field(validator=validators.instance_of(TelegramUser))
    created_at: datetime = attrs.field(
        validator=validators.instance_of(datetime), factory=datetime.now
    )
    recipient_market: Market = attrs.field(validator=validators.instance_of(Market))
    commentary: str = attrs.field(validator=validators.instance_of(str))
    confirmed: ConfirmedStatus = attrs.field(
        validator=validators.instance_of(ConfirmedStatus),
        default=ConfirmedStatus.NOT_PROCESSED,
    )
    order_messages: List[OrderMessage] = attrs.field(factory=list)

    def create(self):
        self.events.append(OrderCreated(dto.order.Order.from_orm(self)))

    def add_order_line(self, order_line: OrderLine):
        self.order_lines.append(order_line)

    def change_confirm_status(self, status: ConfirmedStatus, confirmed_by: User):
        if self.confirmed is not ConfirmedStatus.NOT_PROCESSED:
            raise OrderAlreadyConfirmed()
        self.confirmed = status
        self.events.append(
            OrderConfirmStatusChanged(dto.order.Order.from_orm(self), confirmed_by)
        )

    def add_order_message(self, order_message: OrderMessage):
        self.order_messages.append(order_message)


class OrderCreated(Event):
    def __init__(self, order: dto.Order):
        self.order = order


class OrderConfirmStatusChanged(Event):
    def __init__(self, order: dto.Order, user: User):
        self.order = order
        self.user = user
