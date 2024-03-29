from typing import List
from uuid import UUID

from pydantic import parse_obj_as
from sqlalchemy import func, insert, select, desc
from sqlalchemy.exc import IntegrityError

from app.domain.goods.exceptions.goods import GoodsNotExists
from app.domain.goods.models.goods import Goods
from app.domain.order import dto
from app.domain.order.exceptions.order import (
    OrderAlreadyExists,
    OrderLineGoodsHasIncorrectType,
    OrderNotExists,
)
from app.domain.order.interfaces.persistence import IOrderReader, IOrderRepo
from app.domain.order.models.order import Order, OrderLine
from app.domain.order.value_objects.confirmed_status import ConfirmedStatus
from app.infrastructure.database.repositories.repo import SQLAlchemyRepo


class OrderReader(SQLAlchemyRepo, IOrderReader):
    async def all_orders(self) -> List[dto.Order]:
        ...

    async def order_by_id(self, order_id: UUID) -> Order:
        order = await self.session.get(Order, order_id)

        if not order:
            raise OrderNotExists(f"Order with id {order_id} not exists")

        return dto.Order.from_orm(order)

    async def get_user_orders(
        self, user_id: int, limit: int, offset: int
    ) -> List[dto.Order]:
        query = (
            select(Order)
            .where(Order.creator.has(id=user_id))
            .order_by(desc(Order.created_at))
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(query)
        orders = result.unique().scalars().fetchall()

        return parse_obj_as(List[dto.Order], orders)

    async def get_user_orders_count(self, user_id: int) -> int:
        query = select(func.count(Order.id)).where(Order.creator.has(id=user_id))

        result = await self.session.execute(query)
        count = result.scalar_one()

        return count

    async def get_orders_for_confirmation(self, limit: int, offset: int) -> List[Order]:
        query = (
            select(Order)
            .where(Order.confirmed == ConfirmedStatus.NOT_PROCESSED)
            .order_by(desc(Order.created_at))
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(query)
        orders = result.unique().scalars().fetchall()

        return parse_obj_as(List[dto.Order], orders)

    async def get_orders_for_confirmation_count(self) -> int:
        query = select(func.count(Order.id)).where(
            Order.confirmed == ConfirmedStatus.NOT_PROCESSED
        )

        result = await self.session.execute(query)
        count = result.scalar_one()

        return count

    async def get_all_orders(self, limit: int, offset: int) -> List[dto.Order]:
        query = select(Order).order_by(desc(Order.created_at)).limit(limit).offset(offset)
        result = await self.session.execute(query)
        orders = result.unique().scalars().fetchall()

        return parse_obj_as(List[dto.Order], orders)

    async def get_all_orders_count(self) -> int:
        query = select(func.count(Order.id))
        result = await self.session.execute(query)
        count = result.scalar_one()

        return count


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
            except IntegrityError:
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
        await self.session.flush()
        return new_order

    async def order_by_id(self, order_id: UUID) -> Order:
        order = await self.session.get(Order, order_id)

        if not order:
            raise OrderNotExists(f"Order with id {order_id} not exists")

        return order

    async def edit_order(self, order: Order) -> Order:
        order_id = order.id  # copy order id to access in case of exception
        try:
            await self.session.flush()
            await self.session.refresh(order)
        except IntegrityError as err:
            raise OrderAlreadyExists(
                f"Order with id {order_id} already exists"
            ) from err

        return order
