from typing import Optional
from uuid import UUID

from app.domain.common.dto.base import DTO
from app.domain.goods.models.goods_type import GoodsType


class GoodsCreate(DTO):
    name: str
    type: GoodsType
    parent_id: Optional[UUID]
    sku: Optional[str]


class Goods(DTO):
    id: UUID
    name: str
    type: GoodsType
    parent_id: Optional[UUID]
    sku: Optional[str]
    is_active: bool
