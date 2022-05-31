from __future__ import annotations

from enum import Enum

from sqlalchemy import BIGINT, INT, TEXT, Column
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Table
from sqlalchemy.orm import relationship

from app.domain.access_levels.models import helper
from app.domain.access_levels.models.access_level import AccessLevel, LevelName
from app.domain.user.models.user import TelegramUser

from .base import mapper_registry

user_access_levels = Table(
    "user_access_levels",
    mapper_registry.metadata,
    Column(
        "user_id",
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    ),
    Column(
        "access_level_id",
        ForeignKey("access_level.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    ),
)

access_level_table = Table(
    "access_level",
    mapper_registry.metadata,
    Column("id", INT, primary_key=True, autoincrement=True),
    Column("name", SQLEnum(LevelName), nullable=False),
)

user_table = Table(
    "user",
    mapper_registry.metadata,
    Column("id", BIGINT, primary_key=True),
    Column("name", TEXT, nullable=False),
)

mapper_registry.map_imperatively(
    TelegramUser,
    user_table,
    properties={
        "access_levels": relationship(
            AccessLevel,
            secondary=user_access_levels,
            back_populates="users",
            lazy="selectin",
        )
    },
)
mapper_registry.map_imperatively(
    AccessLevel,
    access_level_table,
    properties={
        "users": relationship(
            TelegramUser,
            secondary=user_access_levels,
            back_populates="access_levels",
        )
    },
)


class UpdatedLevels(Enum):  # ToDo
    BLOCKED = AccessLevel(id=-1, name=LevelName.BLOCKED)
    ADMINISTRATOR = AccessLevel(id=1, name=LevelName.ADMINISTRATOR)
    USER = AccessLevel(id=2, name=LevelName.USER)


helper.Levels = UpdatedLevels


def map_tables():
    pass
