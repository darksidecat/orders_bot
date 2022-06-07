from typing import Any, Dict

import sqlalchemy.orm

from app.domain.common.events.dispatcher import EventDispatcher
from app.domain.user.access_policy import AllowPolicy
from app.tgbot.middlewares.database import Database
from app.tgbot.middlewares.services import Services


async def access_policy_middleware(
    handler,
    event,
    data: Dict[str, Any],
) -> Any:
    data["access_policy"] = AllowPolicy()
    return await handler(event, data)


def setup_event_middlewares(
    dp: EventDispatcher,
    sessionmaker: sqlalchemy.orm.sessionmaker,
):
    dp.notifications.middleware(Database(sessionmaker))
    dp.notifications.middleware(access_policy_middleware)
    dp.notifications.middleware(Services())
