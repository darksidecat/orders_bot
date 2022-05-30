from typing import List, Protocol

from app.domain.user.dto.user import User as UserDTO
from app.domain.user.models.user import TelegramUser


class IUserReader(Protocol):
    async def all_users(self) -> List[UserDTO]:
        ...

    async def user_by_id(self, user_id: int) -> UserDTO:
        ...


class IUserRepo(Protocol):
    async def add_user(self, user: TelegramUser) -> TelegramUser:
        ...

    async def user_by_id(self, user_id: int) -> TelegramUser:
        ...

    async def delete_user(self, user_id: int) -> None:
        ...

    async def edit_user(self, user: TelegramUser) -> TelegramUser:
        ...
