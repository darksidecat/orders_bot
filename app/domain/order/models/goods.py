from __future__ import annotations

import uuid
from typing import List, Optional
from uuid import UUID

import attrs
from attrs import validators

from app.domain.base.models.entity import entity
from app.domain.order.value_objects import GoodsType


@entity
class Goods:
    id: UUID = attrs.field(validator=validators.instance_of(UUID), factory=uuid.uuid4)
    name: str = attrs.field(validator=validators.instance_of(str))
    type: Optional[GoodsType] = attrs.field(
        validator=validators.instance_of(Optional[GoodsType])
    )
    sku: Optional[str] = attrs.field(
        validator=validators.instance_of(Optional[str]), default=None
    )
    is_active: bool = attrs.field(validator=validators.instance_of(bool), default=True)

    parent: Optional[Goods] = attrs.field(default=None, repr=False)
    children: List[Goods] = attrs.field(factory=list, repr=False)
