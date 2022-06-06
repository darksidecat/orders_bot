from  __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from app.domain.common.dto.base import DTO, UNSET
from app.domain.market.dto import Market
from app.domain.user.dto import User


class OrderLine(DTO):
    goods_id: UUID
    quantity: int


class Order(DTO):
    id: UUID
    order_lines: list[OrderLine]
    creator: User
    created_at: datetime
    recipient_market: Market
    commentary: str


class OrderCreate(DTO):
    order_lines: list[OrderLine]
    creator_id: int
    recipient_market_id: UUID
    commentary: str
