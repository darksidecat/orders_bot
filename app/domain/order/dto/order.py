from __future__ import annotations

from datetime import datetime
from uuid import UUID

from app.domain.common.dto.base import DTO
from app.domain.goods.dto import Goods
from app.domain.market.dto import Market
from app.domain.order.models.confirmed_status import ConfirmedStatus
from app.domain.user.dto import User


class OrderLineCreate(DTO):
    goods_id: UUID
    quantity: int


class OrderLine(DTO):
    quantity: int
    goods: Goods


class Order(DTO):
    id: UUID
    order_lines: list[OrderLine]
    creator: User
    created_at: datetime
    recipient_market: Market
    commentary: str
    confirmed: ConfirmedStatus


class OrderCreate(DTO):
    order_lines: list[OrderLineCreate]
    creator_id: int
    recipient_market_id: UUID
    commentary: str
