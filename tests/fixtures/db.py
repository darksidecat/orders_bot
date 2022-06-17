import alembic
import alembic.config
from _pytest.fixtures import fixture
from alembic import command
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import clear_mappers

from app.infrastructure.database.db import sa_sessionmaker, make_connection_string
from app.infrastructure.database.models import map_tables


__all__ = [
    "session_factory",
    "db_wipe",
    "test_db",
    "db_session",
]


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
