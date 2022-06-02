from app.infrastructure.database.models.goods import map_goods
from app.infrastructure.database.models.market import map_market
from app.infrastructure.database.models.order import map_order
from app.infrastructure.database.models.user import map_user


def map_tables():
    map_goods()
    map_market()
    map_order()
    map_user()
