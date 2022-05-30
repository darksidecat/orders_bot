from typing import Type

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.access_levels.interfaces.persistence import IAccessLevelReader
from app.domain.access_levels.interfaces.uow import IAccessLevelUoW
from app.domain.common.interfaces.uow import IUoW
from app.domain.goods.interfaces.persistence import IGoodsReader, IGoodsRepo
from app.domain.goods.interfaces.uow import IGoodsUoW
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


class SQLAlchemyUoW(SQLAlchemyBaseUoW, IUserUoW, IAccessLevelUoW, IGoodsUoW):
    user: IUserRepo
    user_reader = IUserReader
    access_level_reader: IAccessLevelReader
    goods: IGoodsRepo
    goods_reader: IGoodsReader

    def __init__(
        self,
        session: AsyncSession,
        user_repo: Type[IUserRepo],
        user_reader: Type[IUserReader],
        access_level_reader: Type[IAccessLevelReader],
        goods_repo: Type[IGoodsRepo],
        goods_reader: Type[IGoodsReader],
    ):
        self.user = user_repo(session)
        self.user_reader = user_reader(session)
        self.access_level_reader = access_level_reader(session)
        self.goods = goods_repo(session)
        self.goods_reader = goods_reader(session)
        super().__init__(session)
