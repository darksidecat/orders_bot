from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Update
from sqlalchemy.orm import sessionmaker

from app.infrastructure.database.repositories import AccessLevelReader, UserRepo
from app.infrastructure.database.repositories.goods import GoodsReader, GoodsRepo
from app.infrastructure.database.repositories.market import MarketReader, MarketRepo
from app.infrastructure.database.repositories.user import UserReader
from app.infrastructure.database.uow import SQLAlchemyUoW


class Database(BaseMiddleware):
    def __init__(self, sm: sessionmaker) -> None:
        self.Session = sm

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:

        async with self.Session() as session:
            data["session"] = session
            data["uow"] = SQLAlchemyUoW(
                session=session,
                user_repo=UserRepo,
                access_level_reader=AccessLevelReader,
                user_reader=UserReader,
                goods_repo=GoodsRepo,
                goods_reader=GoodsReader,
                market_repo=MarketRepo,
                market_reader=MarketReader,
            )

            return await handler(event, data)
