from _pytest.fixtures import fixture

from app.infrastructure.database.repositories import GoodsReader, GoodsRepo, OrderRepo, OrderReader, MarketRepo, \
    MarketReader, UserRepo, UserReader


__all__ = [
    "goods_reader",
    "goods_repo",
    "order_repo",
    "order_reader",
    "market_repo",
    "market_reader",
    "user_repo",
    "user_reader",
]


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
