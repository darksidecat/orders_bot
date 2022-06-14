import asyncio

import alembic
import alembic.config
from alembic import command
from pytest import fixture
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import clear_mappers

from app.config import load_config
from app.infrastructure.database.db import make_connection_string, sa_sessionmaker
from app.infrastructure.database.models import map_tables
from app.infrastructure.database.repositories import (
    MarketReader,
    MarketRepo,
    OrderReader,
    OrderRepo,
    UserReader,
    UserRepo,
)
from app.infrastructure.database.repositories.goods import GoodsReader, GoodsRepo


@fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@fixture(scope="session")
def config():
    return load_config(env_file=".env.test")


@fixture(scope="session")
def session_factory(config):
    return sa_sessionmaker(config.db)


@fixture(scope="session")
async def db_wipe(session_factory):
    await wipe_db(session_factory=session_factory)


@fixture(scope="session", autouse=True)
def test_db(session_factory, config, db_wipe) -> None:
    clear_mappers()
    cfg = alembic.config.Config()
    cfg.set_main_option("script_location", "app/infrastructure/database/alembic")
    cfg.set_main_option(
        "sqlalchemy.url", make_connection_string(config.db, async_fallback=True)
    )
    command.upgrade(cfg, "head")


@fixture(scope="function")
async def db_session(session_factory, config) -> AsyncSession:
    clear_mappers()
    map_tables()

    async with create_async_engine(
        make_connection_string(db=config.db)
    ).connect() as connect:
        transaction = await connect.begin()
        session: AsyncSession = session_factory(bind=connect)
        await session.begin_nested()

        @event.listens_for(session.sync_session, "after_transaction_end")
        def reopen_savepoint(session, transaction):
            if transaction.nested and not transaction._parent.nested:
                session.begin_nested()

        yield session
        await session.close()
        if transaction.is_active:
            await transaction.rollback()


async def wipe_db(session_factory, schema: str = "public") -> None:
    async with session_factory() as session:
        await session.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE;")
        await session.commit()
        await session.execute(f"CREATE SCHEMA {schema};")
        await session.commit()


@fixture
def goods_reader(db_session):
    return GoodsReader(session=db_session)


@fixture
def goods_repo(db_session):
    return GoodsRepo(session=db_session)


@fixture
def order_repo(db_session):
    return OrderRepo(session=db_session)


@fixture
def order_reader(db_session):
    return OrderReader(session=db_session)


@fixture
def market_repo(db_session):
    return MarketRepo(session=db_session)


@fixture
def market_reader(db_session):
    return MarketReader(session=db_session)


@fixture
def user_repo(db_session):
    return UserRepo(session=db_session)


@fixture
def user_reader(db_session):
    return UserReader(session=db_session)
