import logging
from typing import List
from uuid import UUID

from pydantic import parse_obj_as
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.domain.market import dto
from app.domain.market.exceptions.market import (
    CantDeleteWithOrders,
    MarketAlreadyExists,
    MarketNotExists,
)
from app.domain.market.interfaces.persistence import IMarketReader, IMarketRepo
from app.domain.market.models.market import Market
from app.infrastructure.database.repositories.repo import SQLAlchemyRepo

logger = logging.getLogger(__name__)


class MarketReader(SQLAlchemyRepo, IMarketReader):
    async def all_markets(self, only_active: bool = False) -> List[dto.Market]:
        query = select(Market).order_by(Market.name)

        if only_active:
            query = query.where(Market.is_active.is_(True))

        result = await self.session.execute(query)
        goods = result.scalars().all()

        return parse_obj_as(List[dto.Market], goods)

    async def market_by_id(self, market_id: UUID) -> dto.Market:
        goods = await self.session.get(Market, market_id)

        if not goods:
            raise MarketNotExists(f"Market with id {market_id} not exists")

        return dto.Market.from_orm(goods)


class MarketRepo(SQLAlchemyRepo, IMarketRepo):
    async def _market(self, market_id: UUID) -> Market:
        market = await self.session.get(Market, market_id)

        if not market:
            raise MarketNotExists(f"Market with id {market_id} not exists")

        return market

    async def add_market(self, market: Market) -> Market:
        try:
            self.session.add(market)
            await self.session.flush()
        except IntegrityError as err:
            raise MarketAlreadyExists(
                f"Market with id {market.id} already exists"
            ) from err

        return market

    async def market_by_id(self, market_id: UUID) -> Market:
        return await self._market(market_id)

    async def delete_market(self, market_id: UUID) -> None:
        try:
            market = await self._market(market_id)
            await self.session.delete(market)
            await self.session.flush()
        except IntegrityError as err:
            if "fk_order_recipient_market_id_market" in str(err):
                raise CantDeleteWithOrders(
                    f"Market with id {market_id} can't be deleted as it has orders"
                ) from err
            raise

    async def edit_market(self, market: Market) -> Market:
        market_id = market.id  # copy market id to access in case of exception
        try:
            await self.session.flush()
        except IntegrityError as err:
            raise MarketAlreadyExists(
                f"Market with id {market_id} already exists"
            ) from err

        return market
