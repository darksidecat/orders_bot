from dataclasses import dataclass

from pytest import fixture

from app.domain.access_levels.models.access_level import LevelName
from app.domain.access_levels.models.helper import name_to_access_levels
from app.domain.goods.models.goods import Goods
from app.domain.goods.models.goods_type import GoodsType
from app.domain.market.models.market import Market
from app.domain.order.dto import OrderCreate, OrderLineCreate
from app.domain.order.models.order import Order
from app.domain.user.models.user import TelegramUser
from app.infrastructure.database.repositories import (
    MarketReader,
    MarketRepo,
    OrderRepo,
    UserRepo,
)
from app.infrastructure.database.repositories.goods import GoodsRepo


@dataclass
class OrderWithRelatedData:
    order: Order
    market: Market
    user: TelegramUser
    goods: Goods


@fixture
async def added_order(
    market_repo: MarketRepo,
    market_reader: MarketReader,
    order_repo: OrderRepo,
    goods_repo: GoodsRepo,
    user_repo: UserRepo,
):
    ukraine_market = Market.create(name="Ukraine")
    await market_repo.add_market(ukraine_market)
    await market_repo.session.commit()

    goods = Goods.create(
        name="Good",
        type=GoodsType.GOODS,
        parent=None,
        sku="12345",
    )
    await goods_repo.add_goods(goods)
    await goods_repo.session.commit()

    user = TelegramUser.create(
        id=1,
        name="User",
        access_levels=name_to_access_levels([LevelName.USER, LevelName.ADMINISTRATOR]),
    )
    await user_repo.add_user(user)
    await user_repo.session.commit()

    order = await order_repo.create_order(
        OrderCreate(
            order_lines=[
                OrderLineCreate(
                    goods_id=goods.id,
                    goods_type=goods.type,
                    quantity=1,
                )
            ],
            creator_id=user.id,
            recipient_market_id=ukraine_market.id,
            commentary="commentary",
        )
    )
    await order_repo.session.commit()

    return OrderWithRelatedData(
        order=order,
        market=ukraine_market,
        user=user,
        goods=goods,
    )
