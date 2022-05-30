from enum import Enum, unique

from app.domain.common.models.value_object import value_object


@unique
class LevelName(Enum):
    BLOCKED = "BLOCKED"
    USER = "USER"
    ADMINISTRATOR = "ADMINISTRATOR"


@value_object
class AccessLevel:
    id: int
    name: LevelName
