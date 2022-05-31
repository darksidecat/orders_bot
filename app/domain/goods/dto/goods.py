from typing import Optional
from uuid import UUID

from app.domain.common.dto.base import DTO, UNSET
from app.domain.goods.models.goods_type import GoodsType


class GoodsCreate(DTO):
    name: str
    type: GoodsType
    parent_id: Optional[UUID]
    sku: Optional[str]


class GoodsPatch(DTO):
    id: UUID
    name: Optional[str] = UNSET
    parent_id: Optional[UUID] = UNSET
    sku: Optional[str] = UNSET


class Goods(DTO):
    id: UUID
    name: str
    type: GoodsType
    parent_id: Optional[UUID]
    sku: Optional[str]
    is_active: bool

    @property
    def icon(self):
        return "" if self.type is GoodsType.GOODS else "📁"

    @property
    def active_icon(self):
        return "" if self.is_active else "❌"

    @property
    def sku_text(self):
        return self.sku or ""
