from typing import List
from uuid import UUID

from sqlalchemy import insert

from app.domain.order import dto
from app.domain.order.interfaces.persistence import IOrderReader, IOrderRepo
from app.domain.order.models.order import Order, OrderLine
from app.infrastructure.database.repositories.repo import SQLAlchemyRepo


class OrderReader(SQLAlchemyRepo, IOrderReader):
    async def all_orders(self) -> List[dto.Order]:
        ...

    async def order_by_id(self, goods_id: UUID) -> dto.Order:
        ...


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
            )
            await self.session.execute(query)

        new_order: Order = await self.session.get(Order, new_order_id)

        print(new_order)

        new_order.create()
        return new_order

    async def add_order(self, order: Order) -> Order:
        ...

    async def order_by_id(self, order_id: UUID) -> Order:
        ...

    async def delete_order(self, goods_id: UUID) -> None:
        ...

    async def edit_order(self, goods: Order) -> Order:
        ...
