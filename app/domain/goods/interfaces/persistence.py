from typing import List, Optional, Protocol
from uuid import UUID

from app.domain.goods.dto.goods import Goods as GoodsDTO
from app.domain.goods.models.goods import Goods


class IGoodsReader(Protocol):
    async def goods_in_folder(self, parent_id: Optional[UUID]) -> List[GoodsDTO]:
        ...

    async def get_parent_folder(self, child_id: UUID) -> Optional[GoodsDTO]:
        ...

    async def goods_by_id(self, goods_id: UUID) -> GoodsDTO:
        ...


class IGoodsRepo(Protocol):
    async def add_goods(self, goods: Goods) -> Goods:
        ...

    async def goods_by_id(self, goods_id: UUID) -> Goods:
        ...

    async def delete_goods(self, goods_id: UUID) -> None:
        ...

    async def edit_goods(self, goods: Goods) -> Goods:
        ...
