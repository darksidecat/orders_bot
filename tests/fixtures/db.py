import asyncio

import alembic
import alembic.config
from alembic import command
from alembic.script import ScriptDirectory
from pytest import fixture
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import clear_mappers

from app.infrastructure.database.db import make_connection_string, sa_sessionmaker
from app.infrastructure.database.models import map_tables

__all__ = [
    "session_factory",
    "db_wipe",
    "test_db",
    "db_session",
]


@fixture(scope="session")
def session_factory(config):
    return sa_sessionmaker(config.db, echo=True)


@fixture(scope="session")
def db_wipe(session_factory):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    loop.run_until_complete(wipe_db(session_factory))
    loop.close()


@fixture(scope="session", autouse=True)
def test_db(session_factory, config, db_wipe) -> None:
    cfg = alembic.config.Config()
    cfg.set_main_option("script_location", "app/infrastructure/database/alembic")
    cfg.set_main_option(
        "sqlalchemy.url", make_connection_string(config.db, async_fallback=True)
    )

    revisions_dir = ScriptDirectory.from_config(cfg)

    # Get & sort migrations, from first to last
    revisions = list(revisions_dir.walk_revisions("base", "heads"))
    revisions.reverse()
    for revision in revisions:
        command.upgrade(cfg, revision.revision)
        command.downgrade(cfg, revision.down_revision or "-1")
        command.upgrade(cfg, revision.revision)


@fixture(scope="function")
async def db_session(session_factory, config) -> AsyncSession:
    clear_mappers()
    map_tables()

    async with create_async_engine(
        make_connection_string(db=config.db)
    ).connect() as connect:
        transaction = await connect.begin()
        async_session: AsyncSession = session_factory(bind=connect)
        await async_session.begin_nested()

        @event.listens_for(async_session.sync_session, "after_transaction_end")
        def reopen_nested_transaction(session, transaction):
            if connect.closed:
                return

            if not connect.in_nested_transaction():
                connect.sync_connection.begin_nested()

        yield async_session
        await async_session.close()
        if transaction.is_active:
            await transaction.rollback()


async def wipe_db(session_factory, schema: str = "public") -> None:
    async with session_factory() as session:
        await session.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE;")
        await session.commit()
        await session.execute(f"CREATE SCHEMA {schema};")
        await session.commit()
