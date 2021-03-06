from app.domain.base.interfaces.uow import IUoW
from app.domain.market.interfaces.persistence import IMarketReader, IMarketRepo


class IMarketUoW(IUoW):
    market: IMarketRepo
    market_reader: IMarketReader
