from typing import List

import attrs
from attr import validators

from app.domain.access_levels.models.access_level import AccessLevel
from app.domain.access_levels.models.helper import Levels
from app.domain.common.events.event import Event
from app.domain.common.models.aggregate import Aggregate
from app.domain.common.models.entity import entity
from app.domain.user import dto
from app.domain.user.exceptions.user import (
    BlockedUserWithOtherRole,
    UserWithNoAccessLevels,
)


def list_with_unique_values(access_levels: list):
    return list(set(access_levels))


@entity
class TelegramUser(Aggregate):
    id: int = attrs.field(validator=validators.instance_of(int))
    name: str = attrs.field(validator=validators.instance_of(str))
    access_levels: List[AccessLevel] = attrs.field(converter=list_with_unique_values)

    @classmethod
    def create(cls, id: int, name: str, access_levels: List[AccessLevel]):
        user = TelegramUser(id=id, name=name, access_levels=access_levels)
        user.events.append(UserCreated(dto.User.from_orm(user)))
        return user

    @access_levels.validator
    def validate_access_levels(self, attribute, value):
        if len(value) < 1:
            raise UserWithNoAccessLevels("User must have at least one access level")
        if len(value) > 1 and Levels.BLOCKED.value in value:
            raise BlockedUserWithOtherRole("Blocked user can have only that role")

    def block_user(self) -> None:
        self.access_levels = [
            Levels.BLOCKED.value,
        ]

    @property
    def is_blocked(self) -> bool:
        return Levels.BLOCKED.value in self.access_levels

    @property
    def is_admin(self) -> bool:
        return Levels.ADMINISTRATOR.value in self.access_levels


class UserCreated(Event):
    def __init__(self, user: dto.User):
        self.user = user
