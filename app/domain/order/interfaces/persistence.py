from typing import List, Optional, Protocol
from uuid import UUID

from app.domain.order import dto
from app.domain.order.models.order import Order


class IOrderReader(Protocol):
    async def all_orders(self) -> List[dto.Order]:
        ...

    async def order_by_id(self, goods_id: UUID) -> dto.Order:
        ...


class IOrderRepo(Protocol):
    async def create_order(self, order: dto.OrderCreate) -> Order:
        ...

    async def add_order(self, order: Order) -> Order:
        ...

    async def order_by_id(self, order_id: UUID) -> Order:
        ...

    async def delete_order(self, goods_id: UUID) -> None:
        ...

    async def edit_order(self, goods: Order) -> Order:
        ...
