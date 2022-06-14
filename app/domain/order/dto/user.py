from __future__ import annotations

from app.domain.base.dto.base import DTO


class User(DTO):
    id: int
    name: str
