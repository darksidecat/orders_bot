from enum import Enum, unique
from typing import List

import attrs
from attr import validators

from app.domain.base.models.entity import entity
from app.domain.base.models.value_object import value_object


def list_with_unique_values(access_levels: list):
    return list(set(access_levels))


@unique
class LevelName(Enum):
    BLOCKED = "BLOCKED"
    USER = "USER"
    ADMINISTRATOR = "ADMINISTRATOR"
    CONFIRMATION = "CONFIRMATION"


@value_object
class AccessLevel:
    id: int
    name: LevelName


@entity
class TelegramUser:
    id: int = attrs.field(validator=validators.instance_of(int))
    name: str = attrs.field(validator=validators.instance_of(str))
    access_levels: List[AccessLevel] = attrs.field(converter=list_with_unique_values)
