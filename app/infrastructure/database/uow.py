from typing import Type

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.access_levels.interfaces.persistence import IAccessLevelReader
from app.domain.access_levels.interfaces.uow import IAccessLevelUoW
from app.domain.base.interfaces.uow import IUoW
from app.domain.goods.interfaces.persistence import IGoodsReader, IGoodsRepo
from app.domain.goods.interfaces.uow import IGoodsUoW
from app.domain.market.interfaces.persistence import IMarketReader, IMarketRepo
from app.domain.market.interfaces.uow import IMarketUoW
from app.domain.order.interfaces.persistence import IOrderReader, IOrderRepo
from app.domain.order.interfaces.uow import IOrderUoW
from app.domain.user.interfaces.persistence import IUserReader, IUserRepo
from app.domain.user.interfaces.uow import IUserUoW
from app.infrastructure.database.exception_mapper import exception_mapper


class SQLAlchemyBaseUoW(IUoW):
    def __init__(self, session: AsyncSession):
        self._session = session

    @exception_mapper
    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()


class SQLAlchemyUoW(
    SQLAlchemyBaseUoW, IUserUoW, IAccessLevelUoW, IGoodsUoW, IMarketUoW, IOrderUoW
):
    user: IUserRepo
    user_reader: IUserReader
    access_level_reader: IAccessLevelReader
    goods: IGoodsRepo
    goods_reader: IGoodsReader
    market: IMarketRepo
    market_reader: IMarketReader
    order: IOrderRepo
    order_reader: IOrderReader

    def __init__(
        self,
        session: AsyncSession,
        user_repo: Type[IUserRepo],
        user_reader: Type[IUserReader],
        access_level_reader: Type[IAccessLevelReader],
        goods_repo: Type[IGoodsRepo],
        goods_reader: Type[IGoodsReader],
        market_repo: Type[IMarketRepo],
        market_reader: Type[IMarketReader],
        order_repo: Type[IOrderRepo],
        order_reader: Type[IOrderReader],
    ):
        self.user = user_repo(session)
        self.user_reader = user_reader(session)
        self.access_level_reader = access_level_reader(session)
        self.goods = goods_repo(session)
        self.goods_reader = goods_reader(session)
        self.market = market_repo(session)
        self.market_reader = market_reader(session)
        self.order = order_repo(session)
        self.order_reader = order_reader(session)
        super().__init__(session)
