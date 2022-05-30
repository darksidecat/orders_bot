from typing import List, Protocol
from uuid import uuid4

from app.domain.goods.dto.goods import Goods as GoodsDTO
from app.domain.goods.models.goods import Goods


class IGoodsReader(Protocol):
    async def all_users(self) -> List[GoodsDTO]:
        ...

    async def goods_by_id(self, goods_id: uuid4) -> GoodsDTO:
        ...


class IGoodsRepo(Protocol):
    async def add_goods(self, goods: Goods) -> Goods:
        ...

    async def goods_by_id(self, goods_id: uuid4) -> Goods:
        ...

    async def delete_goods(self, goods_id: uuid4) -> None:
        ...

    async def edit_goods(self, goods: Goods) -> Goods:
        ...
