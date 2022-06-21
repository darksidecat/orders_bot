import argparse
import asyncio
import csv

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from app.domain.goods.models.goods import Goods
from app.domain.goods.models.goods_type import GoodsType
from app.config import load_config
from app.domain.market.models.market import Market
from app.infrastructure.database.db import sa_sessionmaker
from app.infrastructure.database.models import map_tables


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--markets', type=str, required=True, help='path to csv file with markets')
    parser.add_argument('--goods', type=str, required=True, help='path to csv file with goods')
    args = parser.parse_args()
    return {"markets": args.markets, "goods": args.goods}


# import markets from csv file
# csv format:
# market_name

def import_markets(path):
    # read file as csv
    with open(path, 'r') as f:
        reader = csv.reader(f)
        # skip header
        next(reader)
        # read file as csv
        for line in reader:
            market_name = line[0]
            yield market_name

# import goods from csv file
# csv format:
# id, parent_id,type,name,SKU


@dataclass
class Good:
    id: UUID
    parent_id: UUID
    type: GoodsType
    name: str
    SKU: Optional[str]


def import_goods(path):
    # read file as csv
    with open(path, 'r') as f:
        reader = csv.reader(f)
        # skip header
        next(reader)
        # read file as csv
        for line in reader:
            id = UUID(line[0])
            parent_id = UUID(line[1]) if line[1] else None
            type = GoodsType(line[2])
            name = line[3]
            SKU = line[4] if line[4] else None
            yield Good(id, parent_id, type, name, SKU)


async def import_data_to_db(markets, goods):
    map_tables()
    sessionmaker = sa_sessionmaker(load_config(".env.dev").db)
    async with sessionmaker() as session:
        # import markets
        for market_name in markets:
            market = Market(name=market_name)
            session.add(market)
        await session.commit()
        # import goods
        added_goods = {}
        for good in goods:
            db_good = Goods(
                id=good.id,
                type=good.type,
                name=good.name,
                sku=good.SKU,
                parent=added_goods.get(good.parent_id)
            )
            added_goods[db_good.id] = db_good
            session.add(db_good)
            await session.commit()

    print("Data imported to db")


if __name__ == "__main__":
    args = parse_args()
    markets = import_markets(args["markets"])
    goods = import_goods(args["goods"])
    asyncio.run(import_data_to_db(markets, goods))

