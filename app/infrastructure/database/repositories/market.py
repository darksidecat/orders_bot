import logging
from typing import List
from uuid import UUID

from pydantic import parse_obj_as
from sqlalchemy import select

from app.domain.market import dto
from app.domain.market.exceptions.market import MarketNotExists
from app.domain.market.interfaces.persistence import IMarketReader, IMarketRepo
from app.domain.market.models.market import Market
from app.infrastructure.database.exception_mapper import exception_mapper
from app.infrastructure.database.repositories.repo import SQLAlchemyRepo

logger = logging.getLogger(__name__)


class MarketReader(SQLAlchemyRepo, IMarketReader):
    @exception_mapper
    async def all_markets(self, only_active: bool) -> List[dto.Market]:
        query = select(Market).order_by(Market.name)

        if only_active:
            query = query.where(Market.is_active.is_(True))

        result = await self.session.execute(query)
        goods = result.scalars().all()

        return parse_obj_as(List[dto.Market], goods)

    @exception_mapper
    async def market_by_id(self, market_id: UUID) -> dto.Market:
        goods = await self.session.get(Market, market_id)

        if not goods:
            raise MarketNotExists

        return dto.Market.from_orm(goods)


class MarketRepo(SQLAlchemyRepo, IMarketRepo):
    @exception_mapper
    async def _market(self, market_id: UUID) -> Market:
        market = await self.session.get(Market, market_id)

        if not market:
            raise MarketNotExists

        return market

    @exception_mapper
    async def add_market(self, market: Market) -> Market:
        self.session.add(market)
        await self.session.flush()

        return market

    @exception_mapper
    async def market_by_id(self, market_id: UUID) -> Market:
        return await self._market(market_id)

    @exception_mapper
    async def delete_market(self, market_id: UUID) -> None:
        market = await self._market(market_id)
        await self.session.delete(market)
        await self.session.flush()

    @exception_mapper
    async def edit_market(self, market: Market) -> Market:
        await self.session.flush()

        return market
