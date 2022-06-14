import logging
from abc import ABC
from uuid import UUID

from app.domain.base.events.dispatcher import EventDispatcher
from app.domain.base.exceptions.base import AccessDenied
from app.domain.order import dto
from app.domain.order.access_policy import OrderAccessPolicy
from app.domain.order.dto import User
from app.domain.order.exceptions.order import OrderNotExists
from app.domain.order.interfaces.uow import IOrderUoW
from app.domain.order.models.confirmed_status import ConfirmedStatus
from app.domain.order.models.order import Order, OrderMessage

logger = logging.getLogger(__name__)


class OrderUseCase(ABC):
    def __init__(self, uow: IOrderUoW, event_dispatcher: EventDispatcher) -> None:
        self.uow = uow
        self.event_dispatcher = event_dispatcher


class AddOrder(OrderUseCase):
    async def __call__(self, order: dto.OrderCreate) -> dto.Order:
        order = await self.uow.order.create_order(order=order)

        await self.event_dispatcher.publish_events(order.events)
        await self.uow.commit()
        await self.event_dispatcher.publish_notifications(order.events)

        order.events.clear()

        logger.info("Order persisted: id=%s, %s", order.id, order)

        return dto.Order.from_orm(order)


class ChangeConfirmStatus(OrderUseCase):
    async def __call__(
        self, order_id: UUID, confirmed_status: ConfirmedStatus, confirmed_by: User
    ) -> dto.Order:
        order: Order = await self.uow.order.order_by_id(order_id)
        order.change_confirm_status(confirmed_status, confirmed_by=confirmed_by)

        await self.event_dispatcher.publish_events(order.events)
        await self.uow.order.edit_order(order)
        await self.uow.commit()
        await self.event_dispatcher.publish_notifications(order.events)
        order.events.clear()

        return dto.Order.from_orm(order)


class AddOrderMessages(OrderUseCase):
    async def __call__(
        self, order_id: UUID, messages: list[dto.OrderMessageCreate]
    ) -> dto.Order:
        order: Order = await self.uow.order.order_by_id(order_id)

        for message in messages:
            order.add_order_message(
                OrderMessage(message_id=message.message_id, chat_id=message.chat_id)
            )

        await self.uow.order.edit_order(order)
        await self.uow.commit()
        return dto.Order.from_orm(order)


class GetOrder(OrderUseCase):
    async def __call__(self, order_id: UUID) -> dto.Order:
        return await self.uow.order_reader.order_by_id(order_id)


class GetUserOrders(OrderUseCase):
    async def __call__(self, user_id: int, limit: int, offset: int) -> list[dto.Order]:
        return await self.uow.order_reader.get_user_orders(
            user_id=user_id, limit=limit, offset=offset
        )


class GetUserOrdersCount(OrderUseCase):
    async def __call__(self, user_id: int) -> int:
        return await self.uow.order_reader.get_user_orders_count(user_id=user_id)


class GetOrdersForConfirmation(OrderUseCase):
    async def __call__(self, limit: int, offset: int) -> list[dto.Order]:
        return await self.uow.order_reader.get_orders_for_confirmation(
            limit=limit, offset=offset
        )


class GetOrdersForConfirmationCount(OrderUseCase):
    async def __call__(self) -> int:
        return await self.uow.order_reader.get_orders_for_confirmation_count()


class GetAllOrders(OrderUseCase):
    async def __call__(self, limit: int, offset: int) -> list[dto.Order]:
        return await self.uow.order_reader.get_all_orders(limit=limit, offset=offset)


class GetAllOrdersCount(OrderUseCase):
    async def __call__(self) -> int:
        return await self.uow.order_reader.get_all_orders_count()


class OrderService:
    def __init__(
        self,
        uow: IOrderUoW,
        access_policy: OrderAccessPolicy,
        event_dispatcher: EventDispatcher,
    ) -> None:
        self.uow = uow
        self.access_policy = access_policy
        self.event_dispatcher = event_dispatcher

    async def add_order(self, order: dto.OrderCreate) -> dto.Order:
        if not self.access_policy.add_orders():
            raise AccessDenied()
        return await AddOrder(uow=self.uow, event_dispatcher=self.event_dispatcher)(
            order=order
        )

    async def change_confirm_status(
        self, order_id: UUID, confirmed_status: ConfirmedStatus, confirmed_by: User
    ) -> dto.Order:
        if not self.access_policy.confirm_orders():
            raise AccessDenied()
        return await ChangeConfirmStatus(
            uow=self.uow, event_dispatcher=self.event_dispatcher
        )(
            order_id=order_id,
            confirmed_status=confirmed_status,
            confirmed_by=confirmed_by,
        )

    async def add_order_messages(
        self, order_id: UUID, messages: list[dto.OrderMessageCreate]
    ):
        if not self.access_policy.modify_orders():
            raise AccessDenied()
        return await AddOrderMessages(
            uow=self.uow, event_dispatcher=self.event_dispatcher
        )(order_id=order_id, messages=messages)

    async def get_order_by_id(self, order_id: UUID) -> dto.Order:
        try:
            order = await GetOrder(
                uow=self.uow, event_dispatcher=self.event_dispatcher
            )(order_id=order_id)
        except OrderNotExists:
            order = None
        if not self.access_policy.read_order(order=order):
            raise AccessDenied()
        return await GetOrder(uow=self.uow, event_dispatcher=self.event_dispatcher)(
            order_id=order_id
        )

    async def get_user_orders(
        self, user_id: int, limit: int, offset: int
    ) -> list[dto.Order]:
        if not self.access_policy.read_user_orders(user_id=user_id):
            raise AccessDenied()
        return await GetUserOrders(
            uow=self.uow, event_dispatcher=self.event_dispatcher
        )(user_id=user_id, limit=limit, offset=offset)

    async def get_user_orders_count(self, user_id: int) -> int:
        if not self.access_policy.read_user_orders(user_id=user_id):
            raise AccessDenied()
        return await GetUserOrdersCount(
            uow=self.uow, event_dispatcher=self.event_dispatcher
        )(user_id=user_id)

    async def get_orders_for_confirmation(
        self, limit: int, offset: int
    ) -> list[dto.Order]:
        if not self.access_policy.read_all_orders():
            raise AccessDenied()
        return await GetOrdersForConfirmation(
            uow=self.uow, event_dispatcher=self.event_dispatcher
        )(limit=limit, offset=offset)

    async def get_orders_for_confirmation_count(self) -> int:
        if not self.access_policy.read_all_orders():
            raise AccessDenied()
        return await GetOrdersForConfirmationCount(
            uow=self.uow, event_dispatcher=self.event_dispatcher
        )()

    async def get_all_orders(self, limit: int, offset: int) -> list[dto.Order]:
        if not self.access_policy.read_all_orders():
            raise AccessDenied()
        return await GetAllOrders(uow=self.uow, event_dispatcher=self.event_dispatcher)(
            limit=limit, offset=offset
        )

    async def get_all_orders_count(self) -> int:
        if not self.access_policy.read_all_orders():
            raise AccessDenied()
        return await GetAllOrdersCount(
            uow=self.uow, event_dispatcher=self.event_dispatcher
        )()
