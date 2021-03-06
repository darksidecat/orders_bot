import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.dispatcher.fsm.storage.memory import MemoryStorage, SimpleEventIsolation
from aiogram.dispatcher.fsm.storage.redis import DefaultKeyBuilder, RedisStorage
from aiogram_dialog import DialogRegistry

from app.config import load_config
from app.domain.base.events.dispatcher import EventDispatcher
from app.infrastructure.database.db import sa_sessionmaker
from app.infrastructure.database.models import map_tables
from app.tgbot.event_handlers.order import setup_event_handlers
from app.tgbot.event_handlers.setup_middlewares import setup_event_middlewares
from app.tgbot.handlers import register_handlers
from app.tgbot.middlewares import setup_middlewares
from app.tgbot.services.set_commands import set_commands

logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.error("Starting bot")
    config = load_config()

    if config.tg_bot.use_redis:
        storage = RedisStorage.from_url(
            url=f"redis://{config.redis.host}",
            connection_kwargs={
                "db": config.redis.db,
            },
            key_builder=DefaultKeyBuilder(with_destiny=True),
        )
    else:
        storage = MemoryStorage()

    session_factory = sa_sessionmaker(config.db, echo=False)

    bot = Bot(token=config.tg_bot.token, parse_mode="HTML")
    dp = Dispatcher(storage=storage, events_isolation=SimpleEventIsolation())

    dialog_registry = DialogRegistry(dp)

    setup_middlewares(
        dp=dp,
        sessionmaker=session_factory,
    )
    event_dispatcher = EventDispatcher(bot=bot)
    setup_event_handlers(event_dispatcher=event_dispatcher)
    setup_event_middlewares(
        dp=event_dispatcher,
        sessionmaker=session_factory,
    )

    register_handlers(dp=dp, dialog_registry=dialog_registry)

    map_tables()

    try:
        await set_commands(bot, config)
        await bot.get_updates(offset=-1)
        await dp.start_polling(bot, config=config, event_dispatcher=event_dispatcher)
    finally:
        await dp.fsm.storage.close()
        await bot.session.close()


try:
    asyncio.run(main())
except (KeyboardInterrupt, SystemExit):
    logger.error("Bot stopped!")
