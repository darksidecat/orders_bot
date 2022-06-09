import logging
from abc import ABC
from uuid import UUID

from app.domain.common.events.dispatcher import EventDispatcher
from app.domain.common.exceptions.base import AccessDenied
from app.domain.order import dto
from app.domain.order.interfaces.uow import IOrderUoW
from app.domain.order.models.confirmed_status import ConfirmedStatus
from app.domain.order.models.order import Order
from app.domain.user.access_policy import AccessPolicy
from app.domain.user.dto import User

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
        self, order_id: UUID, confirmed: bool, confirmed_by: User
    ) -> dto.Order:
        order: Order = await self.uow.order.order_by_id(order_id)
        if order.confirmed is not ConfirmedStatus.NOT_PROCESSED:
            raise AccessDenied()
        elif confirmed:
            order.change_confirm_status(ConfirmedStatus.YES, confirmed_by=confirmed_by)
        else:
            order.change_confirm_status(ConfirmedStatus.NO, confirmed_by=confirmed_by)

        await self.event_dispatcher.publish_events(order.events)
        await self.uow.order.edit_order(order)
        await self.uow.commit()
        await self.event_dispatcher.publish_notifications(order.events)
        order.events.clear()

        return dto.Order.from_orm(order)


class OrderService:
    def __init__(
        self,
        uow: IOrderUoW,
        access_policy: AccessPolicy,
        event_dispatcher: EventDispatcher,
    ) -> None:
        self.uow = uow
        self.access_policy = access_policy
        self.event_dispatcher = event_dispatcher

    async def add_order(self, order: dto.OrderCreate) -> dto.Order:
        if not self.access_policy.add_order():
            raise AccessDenied()
        return await AddOrder(uow=self.uow, event_dispatcher=self.event_dispatcher)(
            order=order
        )

    async def change_confirm_status(
        self, order_id: UUID, confirmed: bool, confirmed_by: User
    ) -> dto.Order:
        if not self.access_policy.confirm_order():
            raise AccessDenied()
        return await ChangeConfirmStatus(
            uow=self.uow, event_dispatcher=self.event_dispatcher
        )(order_id=order_id, confirmed=confirmed, confirmed_by=confirmed_by)
