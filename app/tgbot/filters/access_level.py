from typing import List, Union

from aiogram.dispatcher.filters import BaseFilter
from aiogram.types import TelegramObject
from pydantic import validator
from sqlalchemy.orm import Session

from app.domain.access_levels.dto.access_level import LevelName
from app.domain.user.dto.user import User


class AccessLevelFilter(BaseFilter):
    access_levels: Union[LevelName, List[LevelName]]

    @validator("access_levels")
    def _validate_access_levels(
        cls, value: Union[LevelName, List[LevelName]]
    ) -> List[LevelName]:
        if isinstance(value, LevelName):
            value = [value]
        return value

    async def __call__(self, obj: TelegramObject, user: User, session: Session) -> bool:
        if not user:
            if not self.access_levels:
                return True
            return False

        return any((level.name in self.access_levels) for level in user.access_levels)
