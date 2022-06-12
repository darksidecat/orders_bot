from __future__ import annotations

from typing import List, Optional, Tuple, Iterable

from pydantic import validator

from app.domain.access_levels.dto.access_level import AccessLevel
from app.domain.access_levels.models.helper import Levels
from app.domain.common.dto.base import DTO


class UserCreate(DTO):
    id: int
    name: str
    access_levels: List[int]


class PatchUserData(DTO):
    id: Optional[int]
    name: Optional[str]
    access_levels: Optional[list[int]]


class UserPatch(DTO):
    id: int
    user_data: PatchUserData


class BaseUser(DTO):
    id: int
    name: str


class User(BaseUser):
    access_levels: Tuple[AccessLevel, ...]

    @validator("access_levels", pre=True)
    def validate_access_levels(cls, v: Iterable[AccessLevel]) -> Tuple[AccessLevel, ...]:
        return tuple(v)

    @property
    def is_blocked(self) -> bool:
        return Levels.BLOCKED.name in [l.name.name for l in self.access_levels]

    @property
    def is_admin(self) -> bool:
        return Levels.ADMINISTRATOR.name in [l.name.name for l in self.access_levels]

    @property
    def can_confirm_order(self) -> bool:
        return Levels.CONFIRMATION.name in [l.name.name for l in self.access_levels]
