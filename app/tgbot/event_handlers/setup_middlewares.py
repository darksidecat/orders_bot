import sqlalchemy.orm

from app.domain.base.events.dispatcher import EventDispatcher
from app.tgbot.middlewares.database import Database


def setup_event_middlewares(
    dp: EventDispatcher,
    sessionmaker: sqlalchemy.orm.sessionmaker,
):
    dp.notifications.middleware(Database(sessionmaker))
