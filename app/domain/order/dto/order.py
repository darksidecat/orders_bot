from __future__ import annotations

from datetime import datetime
from uuid import UUID

from app.domain.common.dto.base import DTO
from app.domain.goods.dto import Goods
from app.domain.goods.models.goods_type import GoodsType
from app.domain.market.dto import Market
from app.domain.order.models.confirmed_status import ConfirmedStatus
from app.domain.user.dto import User


class OrderLineCreate(DTO):
    goods_id: UUID
    goods_type: GoodsType = GoodsType.GOODS
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


class OrderCreate(DTO):
    order_lines: list[OrderLineCreate]
    creator_id: int
    recipient_market_id: UUID
    commentary: str
