import logging
from typing import List, Optional
from uuid import UUID

from pydantic import parse_obj_as
from sqlalchemy import select

from app.domain.goods import dto
from app.domain.goods.exceptions.goods import GoodsNotExists
from app.domain.goods.interfaces.persistence import IGoodsReader, IGoodsRepo
from app.domain.goods.models.goods import Goods
from app.infrastructure.database.exception_mapper import exception_mapper
from app.infrastructure.database.repositories.repo import SQLAlchemyRepo

logger = logging.getLogger(__name__)


class GoodsReader(SQLAlchemyRepo, IGoodsReader):
    @exception_mapper
    async def goods_in_folder(self, parent_id: Optional[UUID]) -> List[dto.Goods]:
        query = (
            select(Goods)
            .where(Goods.parent_id == parent_id)
            .order_by(Goods.type.desc(), Goods.name)
        )

        result = await self.session.execute(query)
        goods = result.scalars().all()

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
        self.session.add(goods)
        await self.session.flush()

        return goods

    @exception_mapper
    async def goods_by_id(self, user_id: UUID) -> Goods:
        return await self._goods(user_id)

    @exception_mapper
    async def delete_goods(self, goods_id: UUID) -> None:
        goods = await self._goods(goods_id)
        await self.session.delete(goods)
        await self.session.flush()

    @exception_mapper
    async def edit_goods(self, goods: Goods) -> Goods:
        await self.session.flush()

        return goods
