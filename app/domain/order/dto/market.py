from __future__ import annotations

from uuid import UUID

from app.domain.base.dto.base import DTO


class Market(DTO):
    id: UUID
    name: str
    is_active: bool

    @property
    def active_icon(self):
        return "" if self.is_active else "❌"
