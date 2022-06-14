from __future__ import annotations

import uuid
from typing import Optional, List
from uuid import UUID

import attrs
from attrs import validators

from app.domain.common.events.event import Event
from app.domain.common.models.aggregate import Aggregate
from app.domain.common.models.entity import entity
from app.domain.goods import dto
from app.domain.goods.exceptions.goods import CantSetFolderSKU, CantMakeInactiveWithActiveChildren, \
    CantMakeActiveWithInactiveParent
from app.domain.goods.models.goods_type import GoodsType


@entity
class Goods(Aggregate):
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

    @classmethod
    def create(
        cls,
        name: str,
        type: GoodsType,
        parent: Optional[Goods] = None,
        sku: str = None,
        is_active: bool = True,
    ) -> Goods:
        goods = Goods(
            name=name,
            type=type,
            parent=parent,
            sku=sku,
            is_active=is_active,
        )
        goods.events.append(GoodsCreated(dto.Goods.from_orm(goods)))

        return goods

    def change_name(self, name: str) -> None:
        self.name = name

    def change_sku(self, sku: str) -> None:
        if self.type == GoodsType.FOLDER:
            raise CantSetFolderSKU()
        self.sku = sku

    def change_active_status(self, is_active: bool) -> None:
        if is_active is False:
            children_statuses = (
                [child.is_active for child in self.children]
            )
            if True in children_statuses:
                raise CantMakeInactiveWithActiveChildren()

        else:
            if self.parent and self.parent.is_active is False:
                raise CantMakeActiveWithInactiveParent()

        self.is_active = is_active


class GoodsCreated(Event):
    def __init__(self, goods: dto.Goods):
        self.goods = goods
