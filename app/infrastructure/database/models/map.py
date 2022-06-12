from sqlalchemy import event

from app.infrastructure.database.models import mapper_registry
from app.infrastructure.database.models.goods import map_goods
from app.infrastructure.database.models.market import map_market
from app.infrastructure.database.models.order import map_order
from app.infrastructure.database.models.user import map_user


def add_events(target, context):
    if not hasattr(target, "_events"):
        setattr(target, "_events", [])


def map_tables():
    map_goods()
    map_market()
    map_order()
    map_user()

    for mapper in mapper_registry.mappers:
        event.listen(mapper, "load", add_events)
