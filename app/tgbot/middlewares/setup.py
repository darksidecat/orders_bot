import sqlalchemy.orm
from aiogram import Dispatcher

from .database import Database
from .services import Services
from .user import UserDB


def setup_middlewares(
    dp: Dispatcher,
    sessionmaker: sqlalchemy.orm.sessionmaker,
):
    dp.update.outer_middleware(Database(sessionmaker))
    dp.update.outer_middleware(UserDB())
    dp.update.outer_middleware(Services())
