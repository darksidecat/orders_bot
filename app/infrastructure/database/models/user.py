from __future__ import annotations

from enum import Enum

from sqlalchemy import BIGINT, INT, TEXT, Column
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Table
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from app.domain.access_levels.models import helper
from app.domain.access_levels.models.access_level import AccessLevel, LevelName
from app.domain.user.models.user import TelegramUser

from .base import mapper_registry


class UserAccessLevelsAssociation:
    user_id: int
    access_level_id: int
    access_level: AccessLevel

    def __init__(self, access_level: AccessLevel):
        self.access_level = access_level


user_access_levels_table = Table(
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


def map_user():
    mapper_registry.map_imperatively(
        UserAccessLevelsAssociation,
        user_access_levels_table,
        properties={
            "access_level": relationship(
                AccessLevel,
                lazy="selectin",
                passive_deletes="all",
            ),
        }

    )

    mapper_registry.map_imperatively(
        TelegramUser,
        user_table,
        properties={
            "orders": relationship(
                "Order",
                back_populates="creator",
                passive_deletes="all",
                lazy="noload",
            ),
            "user_access_levels": relationship(
                UserAccessLevelsAssociation,
                backref="user",
                lazy="selectin",
            ),
        },

    )

    mapper_registry.map_imperatively(
        AccessLevel,
        access_level_table,
    )

    TelegramUser.access_levels = association_proxy(
                "user_access_levels",
                "access_level",

    )

    class UpdatedLevels(Enum):  # ToDo
        BLOCKED = AccessLevel(id=-1, name=LevelName.BLOCKED)
        ADMINISTRATOR = AccessLevel(id=1, name=LevelName.ADMINISTRATOR)
        USER = AccessLevel(id=2, name=LevelName.USER)
        CONFIRMATION = AccessLevel(id=3, name=LevelName.CONFIRMATION)

    helper.Levels = UpdatedLevels
