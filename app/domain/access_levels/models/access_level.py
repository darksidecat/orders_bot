from enum import Enum, unique

from app.domain.base.models.value_object import value_object


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

    def __eq__(self, other):
        return self.id == other.id and self.name == other.name
