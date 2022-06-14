import logging
from typing import List, Optional
from uuid import UUID

from pydantic import parse_obj_as
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.domain.goods import dto
from app.domain.goods.exceptions.goods import (
    CantDeleteWithChildren,
    CantSetSKUForFolder,
    GoodsAlreadyExists,
    GoodsMustHaveSKU,
    GoodsNotExists,
    GoodsTypeCantBeParent,
)
from app.domain.goods.interfaces.persistence import IGoodsReader, IGoodsRepo
from app.domain.goods.models.goods import Goods
from app.infrastructure.database.exception_mapper import exception_mapper
from app.infrastructure.database.repositories.repo import SQLAlchemyRepo

logger = logging.getLogger(__name__)


class GoodsReader(SQLAlchemyRepo, IGoodsReader):
    @exception_mapper
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

    @exception_mapper
    async def goods_by_id(self, goods_id: UUID) -> dto.Goods:
        goods = await self.session.get(Goods, goods_id)

        if not goods:
            raise GoodsNotExists

        return dto.Goods.from_orm(goods)


class GoodsRepo(SQLAlchemyRepo, IGoodsRepo):
    @exception_mapper
    async def _goods(self, goods_id: UUID) -> Goods:
        goods = await self.session.get(Goods, goods_id)
        if not goods:
            raise GoodsNotExists

        return goods

    @exception_mapper
    async def add_goods(self, goods: Goods) -> Goods:
        try:
            self.session.add(goods)
            await self.session.flush()
        except IntegrityError as err:
            if "goods_pkey" in str(err):
                raise GoodsAlreadyExists
            if "fk_goods_goods" in str(err):
                raise GoodsTypeCantBeParent
            if "ck_folder_sku_null" in str(err):
                raise CantSetSKUForFolder()
            if "ck_goods_sku_not_null" in str(err):
                raise GoodsMustHaveSKU()
            raise

        return goods

    @exception_mapper
    async def goods_by_id(self, user_id: UUID) -> Goods:
        return await self._goods(user_id)

    @exception_mapper
    async def delete_goods(self, goods_id: UUID) -> None:
        try:
            goods = await self._goods(goods_id)
            await self.session.delete(goods)
            await self.session.flush()
        except IntegrityError:
            raise CantDeleteWithChildren()

    @exception_mapper
    async def edit_goods(self, goods: Goods) -> Goods:
        try:
            await self.session.flush()
        except IntegrityError:
            raise GoodsAlreadyExists

        return goods
