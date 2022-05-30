from app.domain.access_levels.interfaces.persistence import IAccessLevelReader
from app.domain.common.interfaces.uow import IUoW


class IAccessLevelUoW(IUoW):
    access_level_reader: IAccessLevelReader
