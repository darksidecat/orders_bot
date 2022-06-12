import logging
from abc import ABC
from typing import List

from app.domain.access_levels.models.helper import id_to_access_levels
from app.domain.common.events.dispatcher import EventDispatcher
from app.domain.common.exceptions.base import AccessDenied
from app.domain.user import dto
from app.domain.user.access_policy import AccessPolicy
from app.domain.user.exceptions.user import CantDeleteWithOrders, UserAlreadyExists
from app.domain.user.interfaces.uow import IUserUoW
from app.domain.user.models.user import TelegramUser

logger = logging.getLogger(__name__)


class UserUseCase(ABC):
    def __init__(self, uow: IUserUoW, event_dispatcher: EventDispatcher) -> None:
        self.uow = uow
        self.event_dispatcher = event_dispatcher


class GetUsers(UserUseCase):
    async def __call__(self) -> List[dto.User]:
        users = await self.uow.user_reader.all_users()
        return users


class GetUsersForConfirmation(UserUseCase):
    async def __call__(self) -> List[dto.User]:
        users = await self.uow.user_reader.users_for_confirmation()
        return users


class GetUser(UserUseCase):
    async def __call__(self, user_id: int) -> dto.User:
        """
        Args:
            user_id:

        Returns:
            user
        Raises:
            UserNotExists - if user doesnt exist
        """
        user = await self.uow.user_reader.user_by_id(user_id)
        return user


class AddUser(UserUseCase):
    async def __call__(self, user: dto.UserCreate) -> dto.User:
        """
        Args:
            user: payload for user creation

        Returns:
            created user
        Raises:
            UserAlreadyExists - if user already exist
            AccessLevelNotExist - if user access level not exist
        """
        user = TelegramUser.create(
            id=user.id,
            name=user.name,
            access_levels=id_to_access_levels(user.access_levels),
        )

        try:
            user = await self.uow.user.add_user(user=user)

            await self.event_dispatcher.publish_events(user.events)
            await self.uow.commit()
            await self.event_dispatcher.publish_notifications(user.events)
            user.events.clear()

            logger.info("User persisted: id=%s, %s", user.id, user)

        except UserAlreadyExists:
            logger.error("User already exists: %s", user)
            await self.uow.rollback()
            raise

        return dto.User.from_orm(user)


class DeleteUser(UserUseCase):
    async def __call__(self, user_id: int) -> None:
        """

        Args:
            user_id: user id for deleting

        Raises:
            UserNotExists - if user for deleting doesnt exist


        """
        try:
            await self.uow.user.delete_user(user_id)
            await self.uow.commit()
        except CantDeleteWithOrders:
            await self.uow.rollback()
            raise

        logger.info("User deleted: id=%s,", user_id)


class PatchUser(UserUseCase):
    async def __call__(self, new_user: dto.UserPatch) -> dto.User:
        """
        Use for partially update User data

        Args:
            new_user: data for user editing

        Returns:
            edited user

        Raises:
            UserNotExists - if user for editing doesn't exist
            AccessLevelNotExist - if user access level not exist
            UserAlreadyExists - if already exist user with new user id
        """
        user = await self.uow.user.user_by_id(user_id=new_user.id)

        if new_user.user_data.id:
            user.id = new_user.user_data.id
        if new_user.user_data.name:
            user.name = new_user.user_data.name
        if new_user.user_data.access_levels:
            user.access_levels = id_to_access_levels(new_user.user_data.access_levels)
        try:
            updated_user = await self.uow.user.edit_user(user=user)
            await self.uow.commit()
        except UserAlreadyExists:
            await self.uow.rollback()
            raise

        logger.info("User edited: id=%s,", updated_user.id)

        return dto.User.from_orm(updated_user)


class UserService:
    def __init__(
        self,
        uow: IUserUoW,
        access_policy: AccessPolicy,
        event_dispatcher: EventDispatcher,
    ) -> None:
        self.uow = uow
        self.access_policy = access_policy
        self.event_dispatcher = event_dispatcher

    async def get_users(self) -> List[dto.User]:
        if not self.access_policy.read_users():
            raise AccessDenied()
        return await GetUsers(uow=self.uow, event_dispatcher=self.event_dispatcher)()

    async def get_users_for_confirmation(self) -> List[dto.User]:
        if not self.access_policy.read_users():
            raise AccessDenied()
        return await GetUsersForConfirmation(
            uow=self.uow, event_dispatcher=self.event_dispatcher
        )()

    async def get_user(self, user_id: int) -> dto.User:
        if not (
            self.access_policy.read_users()
            or self.access_policy.read_user_self(user_id)
        ):
            raise AccessDenied()
        return await GetUser(uow=self.uow, event_dispatcher=self.event_dispatcher)(
            user_id=user_id
        )

    async def add_user(self, user: dto.UserCreate) -> dto.User:
        if not self.access_policy.modify_users():
            raise AccessDenied()
        return await AddUser(uow=self.uow, event_dispatcher=self.event_dispatcher)(
            user=user
        )

    async def delete_user(self, user_id: int) -> None:
        if not self.access_policy.modify_users():
            raise AccessDenied()
        return await DeleteUser(uow=self.uow, event_dispatcher=self.event_dispatcher)(
            user_id=user_id
        )

    async def patch_user(self, new_user: dto.UserPatch) -> dto.User:
        if not self.access_policy.modify_users():
            raise AccessDenied()
        return await PatchUser(uow=self.uow, event_dispatcher=self.event_dispatcher)(
            new_user=new_user
        )
