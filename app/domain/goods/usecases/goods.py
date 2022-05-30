import logging
from abc import ABC

from app.domain.common.events.dispatcher import EventDispatcher
from app.domain.common.exceptions.base import AccessDenied
from app.domain.goods import dto
from app.domain.goods.interfaces.uow import IGoodsUoW
from app.domain.goods.models.goods import Goods
from app.domain.user.access_policy import UserAccessPolicy

logger = logging.getLogger(__name__)


class GoodsUseCase(ABC):
    def __init__(self, uow: IGoodsUoW, event_dispatcher: EventDispatcher) -> None:
        self.uow = uow
        self.event_dispatcher = event_dispatcher


class AddGoods(GoodsUseCase):
    async def __call__(self, goods: dto.GoodsCreate) -> dto.Goods:
        """
        Args:
            goods: payload for user creation

        Returns:
            created goods
        Raises:
            GoodsAlreadyExists - if user already exist
        """
        goods = Goods.create(name=goods.name, type=goods.type, parent_id=goods.parent_id, sku=goods.sku)

        goods = await self.uow.goods.add_goods(goods=goods)

        await self.event_dispatcher.publish_events(goods.events)
        await self.uow.commit()
        await self.event_dispatcher.publish_notifications(goods.events)
        goods.events.clear()

        logger.info("Goods persisted: id=%s, %s", goods.id, goods)

        return dto.Goods.from_orm(goods)



class GoodsService:
    def __init__(
            self,
            uow: IGoodsUoW,
            access_policy: UserAccessPolicy,
            event_dispatcher: EventDispatcher,
    ) -> None:
        self.uow = uow
        self.access_policy = access_policy
        self.event_dispatcher = event_dispatcher

    async def add_goods(self, goods: dto.GoodsCreate) -> dto.Goods:
        if not self.access_policy.modify_user():
            raise AccessDenied()
        return await AddGoods(uow=self.uow, event_dispatcher=self.event_dispatcher)(
            goods=goods
        )