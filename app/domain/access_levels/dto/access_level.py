from app.domain.access_levels.models.access_level import LevelName
from app.domain.common.dto.base import DTO


class AccessLevel(DTO):
    id: int
    name: LevelName

    def __hash__(self):
        return hash((type(self), self.id))
