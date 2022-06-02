from typing import Optional
from uuid import UUID

from app.domain.common.dto.base import DTO, UNSET


class MarketCreate(DTO):
    name: str


class MarketPatch(DTO):
    id: UUID
    name: Optional[str] = UNSET
    parent_id: Optional[UUID] = UNSET
    sku: Optional[str] = UNSET


class Market(DTO):
    id: UUID
    name: str
