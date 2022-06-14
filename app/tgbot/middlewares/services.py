from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Update

from app.domain.access_levels.access_policy import UserBasedAccessLevelsAccessPolicy
from app.domain.access_levels.usecases.access_levels import AccessLevelsService
from app.domain.goods.access_policy import UserBasedGoodsAccessPolicy
from app.domain.goods.usecases.goods import GoodsService
from app.domain.market.access_policy import UserBasedMarketAccessPolicy
from app.domain.market.usecases.market import MarketService
from app.domain.order.access_policy import UserBasedOrderAccessPolicy
from app.domain.order.usecases.order import OrderService
from app.domain.user.access_policy import UserBasedUserAccessPolicy
from app.domain.user.dto import User
from app.domain.user.usecases.user import UserService


class Services(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        event_dispatcher = data.get("event_dispatcher")
        uow = data.get("uow")
        user: User = data.get("user")

        data["user_service"] = UserService(
            uow=uow,
            access_policy=UserBasedUserAccessPolicy(user),
            event_dispatcher=event_dispatcher,
        )
        data["access_levels_service"] = AccessLevelsService(
            uow=uow,
            access_policy=UserBasedAccessLevelsAccessPolicy(user),
            event_dispatcher=event_dispatcher,
        )
        data["goods_service"] = GoodsService(
            uow=uow,
            access_policy=UserBasedGoodsAccessPolicy(user),
            event_dispatcher=event_dispatcher,
        )
        data["market_service"] = MarketService(
            uow=uow,
            access_policy=UserBasedMarketAccessPolicy(user),
            event_dispatcher=event_dispatcher,
        )
        data["order_service"] = OrderService(
            uow=uow,
            access_policy=UserBasedOrderAccessPolicy(user),
            event_dispatcher=event_dispatcher,
        )

        return await handler(event, data)
