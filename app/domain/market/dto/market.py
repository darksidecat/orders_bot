from typing import Optional
from uuid import UUID

from app.domain.common.dto.base import DTO, UNSET


class MarketCreate(DTO):
    name: str


class MarketPatch(DTO):
    id: UUID
    name: Optional[str] = UNSET
    is_active: Optional[bool] = UNSET


class Market(DTO):
    id: UUID
    name: str
    is_active: bool

    @property
    def active_icon(self):
        return "" if self.is_active else "❌"
