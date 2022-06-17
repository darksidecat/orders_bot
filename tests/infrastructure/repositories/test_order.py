from app.domain.access_levels.models.access_level import LevelName
from app.domain.goods.models.goods import Goods
from app.domain.goods.models.goods_type import GoodsType
from app.domain.market.models.market import Market
from app.domain.order.dto import OrderCreate, OrderLineCreate
from app.domain.order.models.order import Order, OrderLine
from app.domain.order.models.user import AccessLevel
from app.domain.user.models.user import TelegramUser


class TestOrderRepo:
    async def test_add_order(self, order_repo, market_repo, goods_repo, user_repo):
        market = await market_repo.add_market(Market.create(name="MarketName"))
        market2 = await market_repo.add_market(Market.create(name="MarketName2"))
        goods = await goods_repo.add_goods(
            Goods.create(type=GoodsType.GOODS, name="A-Goods1", sku="A-SKU1")
        )
        user = await user_repo.add_user(
            TelegramUser.create(
                id=1,
                name="UserName",
                access_levels=[AccessLevel(id=-1, name=LevelName.BLOCKED)],
            )
        )

        order: Order = await order_repo.create_order(
            OrderCreate(
                order_lines=[
                    OrderLineCreate(
                        goods_id=goods.id, goods_type=goods.type, quantity=100
                    )
                ],
                creator_id=user.id,
                recipient_market_id=market.id,
                commentary="Commentary",
            )
        )

        await order_repo.session.commit()
        order.recipient_market_id = market2.id
        await order_repo.edit_order(order)
        assert order.recipient_market_id == market2.id
        assert order.recipient_market == market2
        await order_repo.session.commit()

        await order_repo.session.delete(order)
        await order_repo.session.commit()

        order_repo.session.expunge_all()

        assert await order_repo.session.get(Order, order.id) is None
        assert await order_repo.session.get(OrderLine, order.order_lines[0].id) is None
        assert await order_repo.session.get(Market, market.id) is not None
        assert await order_repo.session.get(Market, market2.id) is not None
        assert await order_repo.session.get(Goods, goods.id) is not None
        assert await order_repo.session.get(TelegramUser, user.id) is not None
