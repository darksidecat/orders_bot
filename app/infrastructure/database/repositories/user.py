import logging
from typing import List

from pydantic import parse_obj_as
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.domain.access_levels.exceptions.access_levels import AccessLevelNotExist
from app.domain.access_levels.models.access_level import AccessLevel, LevelName
from app.domain.user import dto
from app.domain.user.exceptions.user import (
    CantDeleteWithOrders,
    UserAlreadyExists,
    UserNotExists,
)
from app.domain.user.interfaces.persistence import IUserReader, IUserRepo
from app.domain.user.models.user import TelegramUser
from app.infrastructure.database.exception_mapper import exception_mapper
from app.infrastructure.database.models.user import UserAccessLevelsAssociation
from app.infrastructure.database.repositories.repo import SQLAlchemyRepo

logger = logging.getLogger(__name__)


class UserReader(SQLAlchemyRepo, IUserReader):
    @exception_mapper
    async def all_users(self) -> List[dto.User]:
        query = select(TelegramUser)

        result = await self.session.execute(query)
        users = result.scalars().all()

        return parse_obj_as(List[dto.User], users)

    async def users_for_confirmation(self) -> List[dto.User]:
        query = select(TelegramUser).where(
            TelegramUser.access_levels.any(name=LevelName.CONFIRMATION)
        )

        result = await self.session.execute(query)
        users = result.scalars().all()

        return parse_obj_as(List[dto.User], users)

    @exception_mapper
    async def user_by_id(self, user_id: int) -> dto.User:
        user = await self.session.get(TelegramUser, user_id)

        if not user:
            raise UserNotExists

        return dto.User.from_orm(user)


class UserRepo(SQLAlchemyRepo, IUserRepo):
    @exception_mapper
    async def _user(self, user_id: int) -> TelegramUser:
        user = await self.session.get(TelegramUser, user_id)

        if not user:
            raise UserNotExists

        return user

    @exception_mapper
    async def _populate_access_levels(self, user: TelegramUser) -> TelegramUser:
        """access_levels = []

        for level in user.access_levels:
            lvl = await self.session.get(AccessLevel, level.id)

            if level in self.session:
                self.session.expunge(level)
            if lvl is not None:
                access_levels.append(lvl)
            else:
                raise AccessLevelNotExist(f"Access level with id {level.id} not found")

        user.access_levels = access_levels"""
        pass
        return user

    @exception_mapper
    async def add_user(self, user: TelegramUser) -> TelegramUser:
        try:
            await self._populate_access_levels(user)
            await self.session.merge(user)
            await self.session.flush()
        except IntegrityError:
            raise UserAlreadyExists

        return user

    @exception_mapper
    async def user_by_id(self, user_id: int) -> TelegramUser:
        return await self._user(user_id)

    @exception_mapper
    async def delete_user(self, user_id: int) -> None:
        try:
            user = await self._user(user_id)
            await self.session.delete(user)
            await self.session.flush()
        except IntegrityError:
            raise CantDeleteWithOrders

    @exception_mapper
    async def edit_user(self, user: TelegramUser) -> TelegramUser:
        try:
            await self._populate_access_levels(user)
            await self.session.merge(user)
            await self.session.flush()
        except IntegrityError as err:
            print(err)
            raise UserAlreadyExists

        return user
