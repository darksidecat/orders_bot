from __future__ import annotations

from typing import Optional
from uuid import UUID

from app.domain.base.dto.base import DTO
from app.domain.order.value_objects import GoodsType


class Goods(DTO):
    id: UUID
    name: str
    type: GoodsType
    sku: Optional[str]
    is_active: bool

    @property
    def icon(self):
        return "📦" if self.type is GoodsType.GOODS else "📁"

    @property
    def active_icon(self):
        return "" if self.is_active else "❌"

    @property
    def sku_text(self):
        return self.sku or ""
