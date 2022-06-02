from typing import List, Protocol
from uuid import UUID

from app.domain.market.dto.market import Market as MarketDTO
from app.domain.market.models.market import Market


class IMarketReader(Protocol):
    async def market_by_id(self, market_id: UUID) -> MarketDTO:
        ...

    async def all_markets(self) -> List[MarketDTO]:
        ...


class IMarketRepo(Protocol):
    async def add_market(self, market: Market) -> Market:
        ...

    async def market_by_id(self, market_id: UUID) -> Market:
        ...

    async def delete_market(self, market_id: UUID) -> None:
        ...

    async def edit_market(self, market: Market) -> Market:
        ...
