import logging
from typing import List, Optional
from uuid import UUID

from pydantic import parse_obj_as
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.domain.goods import dto
from app.domain.goods.exceptions.goods import (
    CantDeleteWithChildren,
    CantDeleteWithOrders,
    CantSetSKUForFolder,
    GoodsAlreadyExists,
    GoodsMustHaveSKU,
    GoodsNotExists,
    GoodsTypeCantBeParent,
)
from app.domain.goods.interfaces.persistence import IGoodsReader, IGoodsRepo
from app.domain.goods.models.goods import Goods
from app.infrastructure.database.repositories.repo import SQLAlchemyRepo

logger = logging.getLogger(__name__)


class GoodsReader(SQLAlchemyRepo, IGoodsReader):
    async def goods_in_folder(
        self, parent_id: Optional[UUID], only_active: bool
    ) -> List[dto.Goods]:
        query = (
            select(Goods)
            .where(Goods.parent_id == parent_id)
            .order_by(Goods.type.desc(), Goods.name)
        )

        if only_active:
            query = query.where(Goods.is_active.is_(True))

        result = await self.session.execute(query)
        goods = result.scalars().unique().all()

        return parse_obj_as(List[dto.Goods], goods)

    async def goods_by_id(self, goods_id: UUID) -> dto.Goods:
        goods = await self.session.get(Goods, goods_id)

        if not goods:
            raise GoodsNotExists(f"Goods with id {goods_id} not exists")

        return dto.Goods.from_orm(goods)


class GoodsRepo(SQLAlchemyRepo, IGoodsRepo):
    async def _goods(self, goods_id: UUID) -> Goods:
        goods = await self.session.get(Goods, goods_id)
        if not goods:
            raise GoodsNotExists(f"Goods with id {goods_id} not exists")

        return goods

    async def add_goods(self, goods: Goods) -> Goods:
        try:
            self.session.add(goods)
            await self.session.flush()
        except IntegrityError as err:
            if "pk_goods" in str(err):
                raise GoodsAlreadyExists(
                    f"Goods with id {goods.id} already exists"
                ) from err
            if "fk_goods_parent_id_goods" in str(
                err
            ) or "ck_goods_parent_type_is_folder" in str(err):
                raise GoodsTypeCantBeParent(
                    f"Goods with id {goods.id} and {goods.type} can't be parent"
                ) from err
            if "ck_goods_folder_sku_null" in str(err):
                raise CantSetSKUForFolder(
                    f"Goods id={goods.id} with {goods.type} type can't have SKU"
                ) from err
            if "ck_goods_goods_sku_not_null" in str(err):
                raise GoodsMustHaveSKU(
                    f"Goods id={goods.id} with {goods.type} type must have SKU"
                ) from err
            raise

        return goods

    async def goods_by_id(self, user_id: UUID) -> Goods:
        return await self._goods(user_id)

    async def delete_goods(self, goods_id: UUID) -> None:
        try:
            goods = await self._goods(goods_id)
            await self.session.delete(goods)
            await self.session.flush()
        except IntegrityError as err:
            if "fk_order_line_goods_id_goods" in str(err):
                raise CantDeleteWithOrders(
                    f"Goods with id {goods_id} can't be deleted as it has orders"
                ) from err
            if "fk_goods_parent_id_goods" in str(err):
                raise CantDeleteWithChildren(
                    f"Goods with id {goods_id} can't be deleted as it has children"
                ) from err
            raise

    async def edit_goods(self, goods: Goods) -> Goods:
        goods_id = goods.id  # copy goods id to access in case of exception
        try:
            await self.session.flush()
        except IntegrityError as err:
            raise GoodsAlreadyExists(
                f"Goods with id {goods_id} already exists"
            ) from err
        return goods
