import logging
from abc import ABC
from typing import List, Optional
from uuid import UUID

from pydantic import parse_obj_as

from app.domain.common.dto.base import UNSET
from app.domain.common.events.dispatcher import EventDispatcher
from app.domain.common.exceptions.base import AccessDenied
from app.domain.goods import dto
from app.domain.goods.exceptions.goods import (
    CantDeleteWithChildren,
    GoodsAlreadyExists,
    GoodsNotExists,
)
from app.domain.goods.interfaces.uow import IGoodsUoW
from app.domain.goods.models.goods import Goods
from app.domain.user.access_policy import AccessPolicy

logger = logging.getLogger(__name__)


class GoodsUseCase(ABC):
    def __init__(self, uow: IGoodsUoW, event_dispatcher: EventDispatcher) -> None:
        self.uow = uow
        self.event_dispatcher = event_dispatcher


class AddGoods(GoodsUseCase):
    async def __call__(self, goods: dto.GoodsCreate) -> dto.Goods:
        """
        Args:
            goods: payload for user creation

        Returns:
            created goods
        Raises:
            GoodsAlreadyExists - if user already exist
        """
        try:
            parent = await self.uow.goods.goods_by_id(goods.parent_id)
        except GoodsNotExists:
            parent = None
        goods = Goods.create(
            name=goods.name, type=goods.type, parent=parent, sku=goods.sku
        )

        try:
            goods = await self.uow.goods.add_goods(goods=goods)

            await self.event_dispatcher.publish_events(goods.events)
            await self.uow.commit()
            await self.event_dispatcher.publish_notifications(goods.events)
            goods.events.clear()

            logger.info("Goods persisted: id=%s, %s", goods.id, goods)
        except GoodsAlreadyExists:
            logger.error("Goods already exists: %s", goods)
            await self.uow.rollback()
            raise

        return dto.Goods.from_orm(goods)


class GetGoodsInFolder(GoodsUseCase):
    async def __call__(
        self, parent_id: Optional[UUID], only_active: bool
    ) -> list[dto.Goods]:
        goods = await self.uow.goods_reader.goods_in_folder(
            parent_id=parent_id, only_active=only_active
        )
        return parse_obj_as(List[dto.Goods], goods)


class GetGoods(GoodsUseCase):
    async def __call__(self, goods_id: Optional[UUID]) -> dto.Goods:
        goods = await self.uow.goods_reader.goods_by_id(goods_id)
        return dto.Goods.from_orm(goods)


class DeleteGoods(GoodsUseCase):
    async def __call__(self, goods_id: Optional[UUID]) -> None:
        try:
            await self.uow.goods.delete_goods(goods_id)
        except CantDeleteWithChildren:
            await self.uow.rollback()
            raise
        await self.uow.commit()


class PatchGoods(GoodsUseCase):
    async def __call__(self, patch_goods_data: dto.GoodsPatch) -> dto.Goods:
        goods = await self.uow.goods.goods_by_id(patch_goods_data.id)

        if patch_goods_data.name is not UNSET:
            goods.change_name(patch_goods_data.name)
        if patch_goods_data.sku is not UNSET:
            goods.change_sku(patch_goods_data.sku)

        if patch_goods_data.is_active is not UNSET:
            goods.change_active_status(patch_goods_data.is_active)

        await self.uow.goods.edit_goods(goods=goods)
        await self.uow.commit()
        return dto.Goods.from_orm(goods)


class GoodsService:
    def __init__(
        self,
        uow: IGoodsUoW,
        access_policy: AccessPolicy,
        event_dispatcher: EventDispatcher,
    ) -> None:
        self.uow = uow
        self.access_policy = access_policy
        self.event_dispatcher = event_dispatcher

    async def add_goods(self, goods: dto.GoodsCreate) -> dto.Goods:
        if not self.access_policy.modify_goods():
            raise AccessDenied()
        return await AddGoods(uow=self.uow, event_dispatcher=self.event_dispatcher)(
            goods=goods
        )

    async def get_goods_by_id(self, goods_id: UUID) -> dto.Goods:
        if not self.access_policy.read_goods():
            raise AccessDenied()
        return await GetGoods(uow=self.uow, event_dispatcher=self.event_dispatcher)(
            goods_id=goods_id
        )

    async def get_goods_in_folder(
        self, parent_id: Optional[UUID], only_active: bool
    ) -> list[dto.Goods]:
        if not self.access_policy.read_goods():
            raise AccessDenied()
        return await GetGoodsInFolder(
            uow=self.uow, event_dispatcher=self.event_dispatcher
        )(parent_id=parent_id, only_active=only_active)

    async def delete_goods(self, goods_id: UUID) -> None:
        if not self.access_policy.modify_goods():
            raise AccessDenied()
        return await DeleteGoods(uow=self.uow, event_dispatcher=self.event_dispatcher)(
            goods_id=goods_id
        )

    async def patch_goods(self, patch_goods_data: dto.GoodsPatch) -> dto.Goods:
        if not self.access_policy.modify_goods():
            raise AccessDenied()
        return await PatchGoods(uow=self.uow, event_dispatcher=self.event_dispatcher)(
            patch_goods_data=patch_goods_data
        )
