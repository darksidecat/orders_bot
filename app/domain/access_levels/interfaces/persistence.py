from asyncio import Protocol

from app.domain.access_levels import dto


class IAccessLevelReader(Protocol):
    async def all_access_levels(self) -> list[dto.AccessLevel]:
        ...

    async def user_access_levels(self, user_id: int) -> list[dto.access_level]:
        ...
