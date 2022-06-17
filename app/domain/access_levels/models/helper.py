from enum import Enum
from typing import Iterable

from app.domain.access_levels.exceptions.access_levels import AccessLevelNotExist
from app.domain.access_levels.models.access_level import AccessLevel, LevelName


class Levels(Enum):
    BLOCKED = AccessLevel(id=-1, name=LevelName.BLOCKED)
    ADMINISTRATOR = AccessLevel(id=1, name=LevelName.ADMINISTRATOR)
    USER = AccessLevel(id=2, name=LevelName.USER)
    CONFIRMATION = AccessLevel(id=3, name=LevelName.CONFIRMATION)


def id_to_access_levels(level_ids: Iterable[int]):
    levels_map = {level.value.id: level.value for level in Levels}

    if not set(level_ids).issubset(levels_map):
        not_found_levels = set(level_ids).difference(levels_map)
        raise AccessLevelNotExist(
            f"Access levels with ids: {not_found_levels} not found"
        )
    else:
        return list(levels_map[level] for level in level_ids)


def name_to_access_levels(level_names: Iterable[LevelName]):
    levels_map = {level.value.name: level.value for level in Levels}

    if not set(level_names).issubset(levels_map):
        not_found_levels = set(level_names).difference(levels_map)
        raise AccessLevelNotExist(
            f"Access levels with names: {not_found_levels} not found"
        )
    else:
        return list(levels_map[level] for level in level_names)
