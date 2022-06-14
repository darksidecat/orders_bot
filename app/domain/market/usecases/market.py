import logging
from abc import ABC
from typing import List
from uuid import UUID

from app.domain.base.dto.base import UNSET
from app.domain.base.events.dispatcher import EventDispatcher
from app.domain.base.exceptions.base import AccessDenied
from app.domain.market import dto
from app.domain.market.access_policy import UserBasedMarketAccessPolicy
from app.domain.market.exceptions.market import (
    CantDeleteWithOrders,
    MarketAlreadyExists,
)
from app.domain.market.interfaces.uow import IMarketUoW
from app.domain.market.models.market import Market

logger = logging.getLogger(__name__)


class MarketUseCase(ABC):
    def __init__(self, uow: IMarketUoW, event_dispatcher: EventDispatcher) -> None:
        self.uow = uow
        self.event_dispatcher = event_dispatcher


class GetAllMarkets(MarketUseCase):
    async def __call__(self, only_active: bool) -> List[dto.Market]:
        markets = await self.uow.market_reader.all_markets(only_active=only_active)
        return [dto.Market.from_orm(market) for market in markets]


class GetMarket(MarketUseCase):
    async def __call__(self, market_id: UUID) -> dto.Market:
        market = await self.uow.market_reader.market_by_id(market_id)
        return market


class AddMarket(MarketUseCase):
    async def __call__(self, market: dto.MarketCreate) -> Market:

        market = Market.create(name=market.name)

        try:
            market = await self.uow.market.add_market(market)
            await self.event_dispatcher.publish_events(market.events)
            await self.uow.commit()
            await self.event_dispatcher.publish_notifications(market.events)
            market.events.clear()

            logger.info("Market persisted: id=%s, %s", market.id, market)
        except MarketAlreadyExists:
            logger.info("Market already exists: %s", market)
            await self.uow.rollback()
            raise

        return dto.Market.from_orm(market)


class PatchMarket(MarketUseCase):
    async def __call__(self, patch_market_data: dto.MarketPatch) -> Market:
        market = await self.uow.market.market_by_id(patch_market_data.id)

        if patch_market_data.name is not UNSET:
            market.name = patch_market_data.name
        if patch_market_data.is_active is not UNSET:
            market.is_active = patch_market_data.is_active

        await self.uow.market.edit_market(market)
        await self.uow.commit()

        return dto.Market.from_orm(market)


class DeleteMarket(MarketUseCase):
    async def __call__(self, market_id: UUID) -> None:
        try:
            await self.uow.market.delete_market(market_id)
            await self.uow.commit()
        except CantDeleteWithOrders:
            await self.uow.rollback()
            raise


class MarketService:
    def __init__(
        self,
        uow: IMarketUoW,
        access_policy: UserBasedMarketAccessPolicy,
        event_dispatcher: EventDispatcher,
    ) -> None:
        self.uow = uow
        self.access_policy = access_policy
        self.event_dispatcher = event_dispatcher

    async def get_all_markets(self, only_active: bool) -> List[dto.Market]:
        if not self.access_policy.read_markets():
            raise AccessDenied()
        return await GetAllMarkets(self.uow, self.event_dispatcher)(
            only_active=only_active
        )

    async def get_market_by_id(self, market_id: UUID):
        if not self.access_policy.read_markets():
            raise AccessDenied()
        return await GetMarket(self.uow, self.event_dispatcher)(market_id)

    async def add_market(self, market: dto.MarketCreate) -> Market:
        if not self.access_policy.modify_markets():
            raise AccessDenied()
        return await AddMarket(self.uow, self.event_dispatcher)(market)

    async def patch_market(self, market: dto.MarketPatch) -> Market:
        if not self.access_policy.modify_markets():
            raise AccessDenied()
        return await PatchMarket(self.uow, self.event_dispatcher)(market)

    async def delete_market(self, market_id: UUID):
        if not self.access_policy.modify_markets():
            raise AccessDenied()
        return await DeleteMarket(self.uow, self.event_dispatcher)(market_id)
