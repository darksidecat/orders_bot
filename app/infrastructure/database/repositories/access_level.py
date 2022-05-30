from typing import List

from pydantic import parse_obj_as
from sqlalchemy import select

from app.domain.access_levels import dto
from app.domain.access_levels.interfaces.persistence import IAccessLevelReader
from app.domain.access_levels.models.access_level import AccessLevel
from app.domain.user.exceptions.user import UserNotExists
from app.domain.user.models.user import TelegramUser
from app.infrastructure.database.exception_mapper import exception_mapper
from app.infrastructure.database.repositories.repo import SQLAlchemyRepo


class AccessLevelReader(SQLAlchemyRepo, IAccessLevelReader):
    @exception_mapper
    async def all_access_levels(self) -> List[dto.AccessLevel]:
        query = select(AccessLevel)
        result = await self.session.execute(query)
        access_levels = result.scalars().all()

        return parse_obj_as(List[dto.AccessLevel], access_levels)

    @exception_mapper
    async def user_access_levels(self, user_id: int) -> List[dto.AccessLevel]:
        user = await self.session.get(TelegramUser, user_id)

        if not user:
            raise UserNotExists

        return parse_obj_as(List[dto.AccessLevel], user.access_levels)
