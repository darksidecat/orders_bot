from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import DB


def make_connection_string(db: DB, async_fallback: bool = False) -> str:
    result = (
        f"postgresql+asyncpg://{db.user}:{db.password}@{db.host}:{db.port}/{db.name}"
    )
    if async_fallback:
        result += "?async_fallback=True"
    return result


def sa_sessionmaker(db: DB, echo: bool = False) -> sessionmaker:
    """
    Make sessionmaker
    :param driver: dialect+driver
    :param db_path: database path and credential
    :return: sessionmaker
    :rtype: sqlalchemy.orm.sessionmaker
    """
    engine = create_async_engine(make_connection_string(db), echo=echo)
    return sessionmaker(
        bind=engine,
        expire_on_commit=False,
        class_=AsyncSession,
        future=True,
        autoflush=False,
    )
