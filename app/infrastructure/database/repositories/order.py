from typing import List
from uuid import UUID

from asyncpg import CheckViolationError
from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError

from app.domain.goods.exceptions.goods import GoodsNotExists
from app.domain.goods.models.goods import Goods
from app.domain.goods.models.goods_type import GoodsType
from app.domain.order import dto
from app.domain.order.exceptions.order import (
    OrderLineGoodsHasIncorrectType,
    OrderNotExists,
)
from app.domain.order.interfaces.persistence import IOrderReader, IOrderRepo
from app.domain.order.models.order import Order, OrderLine
from app.infrastructure.database.repositories.repo import SQLAlchemyRepo


class OrderReader(SQLAlchemyRepo, IOrderReader):
    async def all_orders(self) -> List[dto.Order]:
        ...

    async def order_by_id(self, order_id: UUID) -> Order:
        order = await self.session.get(Order, order_id)

        if not order:
            raise OrderNotExists(f"Order with id {order_id} not exists")

        return dto.Order.from_orm(order)


class OrderRepo(SQLAlchemyRepo, IOrderRepo):
    async def create_order(self, order: dto.OrderCreate) -> Order:
        query = (
            insert(Order)
            .values(
                creator_id=order.creator_id,
                recipient_market_id=order.recipient_market_id,
                commentary=order.commentary,
            )
            .returning(Order.id)
        )
        result = await self.session.execute(query)
        new_order_id = result.scalar_one()

        for line in order.order_lines:
            query = insert(OrderLine).values(
                order_id=new_order_id,
                goods_id=line.goods_id,
                quantity=line.quantity,
                goods_type=line.goods_type,
            )
            try:
                await self.session.execute(query)
            except IntegrityError as err:
                await self.session.rollback()
                goods = await self.session.get(Goods, line.goods_id)
                if not goods:
                    raise GoodsNotExists(f"Goods with id {line.goods_id} not exists")
                else:
                    raise OrderLineGoodsHasIncorrectType(
                        f"Goods with id {line.goods_id} is {goods.type} type, not GoodsType.GOODS"
                    )

        new_order: Order = await self.session.get(Order, new_order_id)

        new_order.create()
        return new_order

    async def order_by_id(self, order_id: UUID) -> Order:
        order = await self.session.get(Order, order_id)

        if not order:
            raise OrderNotExists(f"Order with id {order_id} not exists")

        return order

    async def edit_order(self, order: Order) -> Order:
        await self.session.flush()
        return order
