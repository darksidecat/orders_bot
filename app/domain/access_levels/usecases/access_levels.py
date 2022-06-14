from typing import List

from app.domain.access_levels.access_policy import AccessLevelsAccessPolicy
from app.domain.access_levels.dto.access_level import AccessLevel
from app.domain.access_levels.interfaces.uow import IAccessLevelUoW
from app.domain.base.events.dispatcher import EventDispatcher
from app.domain.base.exceptions.base import AccessDenied


class AccessLevelsUseCase:
    def __init__(self, uow: IAccessLevelUoW, event_dispatcher: EventDispatcher) -> None:
        self.uow = uow
        self.event_dispatcher = event_dispatcher


class GetAccessLevels(AccessLevelsUseCase):
    async def __call__(self) -> List[AccessLevel]:
        """

        Returns: List of AccessLevel

        """
        return await self.uow.access_level_reader.all_access_levels()


class GetUserAccessLevels(AccessLevelsUseCase):
    async def __call__(self, user_id: int) -> List[AccessLevel]:
        """
        Use for getting user access levels

        Args:
            user_id: user id

        Returns: List of AccessLevel

        Raises:
            UserNotExists - if user not exist

        """
        return await self.uow.access_level_reader.user_access_levels(user_id)


class AccessLevelsService:
    def __init__(
        self,
        uow: IAccessLevelUoW,
        access_policy: AccessLevelsAccessPolicy,
        event_dispatcher: EventDispatcher,
    ) -> None:
        self.uow = uow
        self.access_policy = access_policy
        self.event_dispatcher = event_dispatcher

    async def get_access_levels(self) -> List[AccessLevel]:
        if not self.access_policy.read_access_levels():
            raise AccessDenied()
        return await GetAccessLevels(
            uow=self.uow, event_dispatcher=self.event_dispatcher
        )()

    async def get_user_access_levels(self, user_id: int) -> List[AccessLevel]:
        if not self.access_policy.read_access_levels():
            raise AccessDenied()
        return await GetUserAccessLevels(
            uow=self.uow, event_dispatcher=self.event_dispatcher
        )(user_id=user_id)
