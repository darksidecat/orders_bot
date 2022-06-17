from __future__ import annotations

from datetime import datetime
from uuid import UUID

from app.domain.base.dto.base import DTO
from app.domain.order.dto.goods import Goods
from app.domain.order.dto.market import Market
from app.domain.order.dto.user import User
from app.domain.order.value_objects import ConfirmedStatus, GoodsType


class OrderLineCreate(DTO):
    goods_id: UUID
    goods_type: GoodsType
    quantity: int


class OrderLine(DTO):
    quantity: int
    goods: Goods


class OrderMessageCreate(DTO):
    message_id: int
    chat_id: int


class OrderMessage(DTO):
    message_id: int
    chat_id: int


class OrderCreate(DTO):
    order_lines: list[OrderLineCreate]
    creator_id: int
    recipient_market_id: UUID
    commentary: str


class Order(DTO):
    id: UUID
    order_lines: list[OrderLine]
    creator: User
    created_at: datetime
    recipient_market: Market
    commentary: str
    confirmed: ConfirmedStatus
    order_messages: list[OrderMessage]

    @property
    def confirmed_icon(self):
        if self.confirmed == ConfirmedStatus.YES:
            return "✅"
        elif self.confirmed == ConfirmedStatus.NO:
            return "❌"
        else:
            return ""
