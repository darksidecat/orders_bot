from __future__ import annotations

import uuid
from typing import Optional
from uuid import UUID

import attrs
from attrs import validators

from app.domain.common.events.event import Event
from app.domain.common.models.aggregate import Aggregate
from app.domain.common.models.entity import entity
from app.domain.goods import dto
from app.domain.goods.models.goods_type import GoodsType


@entity
class Goods(Aggregate):
    id: UUID = attrs.field(validator=validators.instance_of(UUID), factory=uuid.uuid4)
    name: str = attrs.field(validator=validators.instance_of(str))
    type: Optional[GoodsType] = attrs.field(
        validator=validators.instance_of(Optional[GoodsType])
    )
    parent_id: Optional[UUID] = attrs.field(
        validator=validators.instance_of(Optional[UUID]), default=None
    )
    sku: Optional[str] = attrs.field(validator=validators.instance_of(Optional[str]))
    is_active: bool = attrs.field(validator=validators.instance_of(bool), default=True)

    @classmethod
    def create(
        cls,
        name: str,
        type: GoodsType,
        parent_id: Optional[UUID] = None,
        sku: str = None,
        is_active: bool = True,
    ) -> Goods:
        goods = Goods(
            name=name,
            type=type,
            parent_id=parent_id,
            sku=sku,
            is_active=is_active,
        )

        goods.events.append(GoodsCreated(dto.Goods.from_orm(goods)))

        return goods


class GoodsCreated(Event):
    def __init__(self, goods: dto.Goods):
        self.goods = goods
