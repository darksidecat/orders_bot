from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Update

from app.domain.access_levels.usecases.access_levels import AccessLevelsService
from app.domain.goods.usecases.goods import GoodsService
from app.domain.market.usecases.market import MarketService
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
        access_policy = data.get("access_policy")

        data["user_service"] = UserService(
            uow=uow, access_policy=access_policy, event_dispatcher=event_dispatcher
        )
        data["access_levels_service"] = AccessLevelsService(
            uow=uow, access_policy=access_policy, event_dispatcher=event_dispatcher
        )
        data["goods_service"] = GoodsService(
            uow=uow, access_policy=access_policy, event_dispatcher=event_dispatcher
        )
        data["market_service"] = MarketService(
            uow=uow, access_policy=access_policy, event_dispatcher=event_dispatcher
        )

        return await handler(event, data)
