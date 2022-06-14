from typing import Any
from unittest.mock import sentinel

from pydantic import BaseModel, Extra


class DTO(BaseModel):
    class Config:
        use_enum_values = False
        extra = Extra.forbid
        frozen = True
        orm_mode = True


UNSET: Any = sentinel.UNSET
