import logging
from abc import ABC

from app.domain.common.events.dispatcher import EventDispatcher
from app.domain.common.exceptions.base import AccessDenied
from app.domain.order import dto
from app.domain.order.interfaces.uow import IOrderUoW
from app.domain.order.models.order import Order
from app.domain.user.access_policy import UserAccessPolicy


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


class OrderService:
    def __init__(
        self,
        uow: IOrderUoW,
        access_policy: UserAccessPolicy,
        event_dispatcher: EventDispatcher,
    ) -> None:
        self.uow = uow
        self.access_policy = access_policy
        self.event_dispatcher = event_dispatcher

    async def add_order(self, order: dto.OrderCreate) -> dto.Order:
        if not self.access_policy.modify_goods():
            raise AccessDenied()
        return await AddOrder(uow=self.uow, event_dispatcher=self.event_dispatcher)(
            order=order
        )
