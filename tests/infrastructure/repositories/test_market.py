import uuid
from uuid import UUID

import pytest

from app.domain.access_levels.models.access_level import LevelName
from app.domain.access_levels.models.helper import name_to_access_levels
from app.domain.goods.models.goods import Goods
from app.domain.goods.models.goods_type import GoodsType
from app.domain.market import dto
from app.domain.market.exceptions.market import (
    CantDeleteWithOrders,
    MarketAlreadyExists,
    MarketNotExists,
)
from app.domain.market.models.market import Market
from app.domain.order.dto import OrderCreate, OrderLineCreate
from app.domain.user.models.user import TelegramUser
from app.infrastructure.database.repositories import (
    GoodsRepo,
    MarketReader,
    MarketRepo,
    OrderRepo,
    UserRepo,
)


class TestMarketReader:
    async def test_all_markets(
        self, market_reader: MarketReader, market_repo: MarketRepo
    ):
        markets = await market_reader.all_markets()
        assert len(markets) == 0

        ukraine_market = Market.create(name="Ukraine")
        poland_market = Market.create(name="Poland")
        await market_repo.add_market(ukraine_market)
        await market_repo.add_market(poland_market)

        await market_repo.session.commit()

        markets = await market_reader.all_markets()
        assert len(markets) == 2

        assert dto.Market.from_orm(ukraine_market) in markets
        assert dto.Market.from_orm(poland_market) in markets

    async def test_all_market_only_active(
        self, market_reader: MarketReader, market_repo: MarketRepo
    ):
        ukraine_market = Market.create(name="Ukraine")
        poland_market = Market.create(name="Poland")
        poland_market.is_active = False
        await market_repo.add_market(ukraine_market)
        await market_repo.add_market(poland_market)

        await market_repo.session.commit()

        markets = await market_reader.all_markets(only_active=True)
        assert len(markets) == 1
        assert dto.Market.from_orm(ukraine_market) in markets

    async def test_market_by_id(
        self, market_reader: MarketReader, market_repo: MarketRepo
    ):
        ukraine_market = Market.create(name="Ukraine")
        await market_repo.add_market(ukraine_market)
        await market_repo.session.commit()

        market = await market_reader.market_by_id(ukraine_market.id)
        assert dto.Market.from_orm(ukraine_market) == market

    async def test_market_by_id_not_found(
        self, market_reader: MarketReader, market_repo: MarketRepo
    ):
        with pytest.raises(MarketNotExists):
            await market_reader.market_by_id(
                UUID("00000000-0000-0000-0000-000000000000")
            )


class TestMarketRepo:
    async def test_add_market(self, market_repo: MarketRepo, market_reader):
        ukraine_market = Market.create(name="Ukraine")
        await market_repo.add_market(ukraine_market)
        await market_repo.session.commit()

        market = await market_repo.market_by_id(ukraine_market.id)
        assert market is ukraine_market

    # ignore identity key conflict
    @pytest.mark.filterwarnings("ignore::sqlalchemy.exc.SAWarning")
    async def test_add_market_already_exists(
        self, market_repo: MarketRepo, market_reader
    ):
        ukraine_market = Market.create(name="Ukraine")
        await market_repo.add_market(ukraine_market)
        await market_repo.session.commit()

        with pytest.raises(MarketAlreadyExists):
            await market_repo.add_market(Market(id=ukraine_market.id, name="Ukraine"))

    async def test_market_by_id(self, market_repo: MarketRepo, market_reader):
        ukraine_market = Market.create(name="Ukraine")
        await market_repo.add_market(ukraine_market)
        await market_repo.session.commit()

        market = await market_repo.market_by_id(ukraine_market.id)
        assert market is ukraine_market

    async def test_market_by_id_not_found(self, market_repo: MarketRepo, market_reader):
        with pytest.raises(MarketNotExists):
            await market_repo.market_by_id(UUID("00000000-0000-0000-0000-000000000000"))

    async def test_delete_market(self, market_repo: MarketRepo, market_reader):
        ukraine_market = Market.create(name="Ukraine")
        await market_repo.add_market(ukraine_market)
        await market_repo.session.commit()

        await market_repo.delete_market(ukraine_market.id)
        await market_repo.session.commit()

        with pytest.raises(MarketNotExists):
            await market_reader.market_by_id(ukraine_market.id)

    async def test_update_market(self, market_repo: MarketRepo, market_reader):
        ukraine_market = Market.create(name="Kyivan Rus")
        await market_repo.add_market(ukraine_market)
        await market_repo.session.commit()

        ukraine_market.name = "Ukraine"
        await market_repo.edit_market(ukraine_market)
        await market_repo.session.commit()

        market = await market_reader.market_by_id(ukraine_market.id)
        assert market.name == "Ukraine"

    async def test_update_market_not_found(
        self, market_repo: MarketRepo, market_reader
    ):
        market = await market_repo.add_market(
            Market(id=UUID("00000000-0000-0000-0000-000000000000"), name="Ukraine")
        )
        market_2 = await market_repo.add_market(
            Market(id=uuid.uuid4(), name="Australia")
        )
        await market_repo.session.commit()

        market_2.id = market.id
        with pytest.raises(MarketAlreadyExists):
            await market_repo.edit_market(market_2)
            await market_repo.session.commit()

    async def test_cant_delete_market_with_orders(
        self,
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
            access_levels=name_to_access_levels(
                [LevelName.USER, LevelName.ADMINISTRATOR]
            ),
        )
        await user_repo.add_user(user)
        await user_repo.session.commit()

        await order_repo.create_order(
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
        await market_repo.session.commit()

        with pytest.raises(CantDeleteWithOrders):
            await market_repo.delete_market(ukraine_market.id)
            await market_repo.session.commit()
