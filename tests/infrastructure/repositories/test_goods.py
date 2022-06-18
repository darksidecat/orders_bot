from uuid import UUID

import pytest
from sqlalchemy import func, select

from app.domain.goods.exceptions.goods import (
    CantDeleteWithChildren,
    CantDeleteWithOrders,
    CantSetSKUForFolder,
    GoodsAlreadyExists,
    GoodsMustHaveSKU,
    GoodsNotExists,
    GoodsTypeCantBeParent,
)
from app.domain.goods.models.goods import Goods
from app.domain.goods.models.goods_type import GoodsType
from app.infrastructure.database.repositories.goods import GoodsReader, GoodsRepo
from tests.infrastructure.repositories.conftest import OrderWithRelatedData


class TestGoodsReader:
    async def test_goods_in_folder(
        self, goods_repo: GoodsRepo, goods_reader: GoodsReader
    ):
        folder1 = await goods_repo.add_goods(
            Goods.create(type=GoodsType.FOLDER, name="B-Folder1")
        )
        folder2 = await goods_repo.add_goods(
            Goods.create(type=GoodsType.FOLDER, name="B-Folder2")
        )
        goods1 = await goods_repo.add_goods(
            Goods.create(type=GoodsType.GOODS, name="A-Goods1", sku="A-SKU1")
        )
        goods2 = await goods_repo.add_goods(
            Goods.create(
                type=GoodsType.GOODS,
                name="A-Goods2",
                sku="A-SKU2",
                parent=folder1,
            )
        )
        await goods_repo.session.commit()

        goods = await goods_reader.goods_in_folder(parent_id=None, only_active=False)
        assert [g.id for g in goods] == [folder1.id, folder2.id, goods1.id]

        goods = await goods_reader.goods_in_folder(
            parent_id=folder1.id, only_active=False
        )
        await goods_repo.session.commit()

        assert [g.id for g in goods] == [goods2.id]

    async def test_goods_in_folder_active_false(self, goods_repo, goods_reader):
        folder1 = await goods_repo.add_goods(
            Goods.create(type=GoodsType.FOLDER, name="B-Folder1")
        )
        goods1 = await goods_repo.add_goods(
            Goods.create(type=GoodsType.GOODS, name="A-Goods1", sku="A-SKU1")
        )
        await goods_repo.session.commit()

        goods = await goods_reader.goods_in_folder(parent_id=None, only_active=False)
        assert [g.id for g in goods] == [folder1.id, goods1.id]

        goods1.change_active_status(False)
        await goods_repo.session.commit()
        goods = await goods_reader.goods_in_folder(parent_id=None, only_active=True)
        assert [g.id for g in goods] == [folder1.id]

    async def test_goods_by_id(self, goods_repo, goods_reader):
        goods = await goods_repo.add_goods(
            Goods.create(type=GoodsType.GOODS, name="A-Goods1", sku="A-SKU1")
        )
        await goods_repo.session.commit()

        goods = await goods_reader.goods_by_id(goods.id)
        assert goods.id == goods.id


class TestGoodsRepo:
    async def test_add_goods(self, goods_repo):
        goods = await goods_repo.add_goods(
            Goods.create(name="GoodsName", type=GoodsType.GOODS, sku="123")
        )
        await goods_repo.session.commit()

        goods_in_db = await goods_repo.session.get(Goods, goods.id)
        assert goods_in_db is goods

        all_goods_count = (
            await goods_repo.session.execute(select(func.count(Goods.id)))
        ).scalar()
        assert all_goods_count == 1

    async def test_add_goods_with_goods_type_as_parent_exception(self, goods_repo):
        goods_type = await goods_repo.add_goods(
            Goods.create(name="GoodsType", type=GoodsType.GOODS, sku="123")
        )
        await goods_repo.session.commit()
        with pytest.raises(GoodsTypeCantBeParent):
            await goods_repo.add_goods(
                Goods.create(
                    name="GoodsName",
                    type=GoodsType.GOODS,
                    sku="123",
                    parent=goods_type,
                )
            )
            await goods_repo.session.commit()

    # ignore identity key conflict
    @pytest.mark.filterwarnings("ignore::sqlalchemy.exc.SAWarning")
    async def test_add_goods_duplicate_id_exception(self, goods_repo):
        goods = await goods_repo.add_goods(
            Goods.create(name="GoodsName", type=GoodsType.GOODS, sku="123")
        )
        await goods_repo.session.commit()
        with pytest.raises(GoodsAlreadyExists):
            await goods_repo.add_goods(
                Goods(id=goods.id, name="GoodsName", type=GoodsType.GOODS, sku="123")
            )
            await goods_repo.session.commit()

    async def test_add_goods_sku_exception(self, goods_repo):
        with pytest.raises(GoodsMustHaveSKU):
            await goods_repo.add_goods(
                Goods.create(name="GoodsName", type=GoodsType.GOODS)
            )
            await goods_repo.session.commit()

    async def test_add_goods_sku_exception_2(self, goods_repo):
        with pytest.raises(CantSetSKUForFolder):
            await goods_repo.add_goods(
                Goods.create(name="GoodsName", type=GoodsType.FOLDER, sku="123")
            )
            await goods_repo.session.commit()

    async def test_goods_by_id(self, goods_repo):
        goods = await goods_repo.add_goods(
            Goods.create(name="GoodsName", type=GoodsType.GOODS, sku="123")
        )
        goods2 = await goods_repo.add_goods(
            Goods.create(name="GoodsName2", type=GoodsType.GOODS, sku="123")
        )
        await goods_repo.session.commit()

        goods_in_db = await goods_repo.goods_by_id(goods.id)

        assert goods_in_db is goods
        assert goods_in_db is not goods2

    async def test_goods_by_id_exception(self, goods_repo):
        await goods_repo.add_goods(
            Goods.create(name="GoodsName", type=GoodsType.GOODS, sku="123")
        )
        await goods_repo.session.commit()

        with pytest.raises(GoodsNotExists):
            await goods_repo.goods_by_id(UUID("00000000-0000-0000-0000-000000000000"))
            await goods_repo.session.commit()

    async def test_delete_goods(self, goods_repo):
        goods = await goods_repo.add_goods(
            Goods.create(name="GoodsName", type=GoodsType.GOODS, sku="123")
        )
        await goods_repo.session.commit()

        await goods_repo.delete_goods(goods.id)
        await goods_repo.session.commit()

        goods_in_db = await goods_repo.session.get(Goods, goods.id)
        assert goods_in_db is None

        all_goods_count = (
            await goods_repo.session.execute(select(func.count(Goods.id)))
        ).scalar()
        assert all_goods_count == 0

    async def test_delete_goods_exception_goods_not_exist(self, goods_repo):
        await goods_repo.add_goods(
            Goods.create(name="GoodsName", type=GoodsType.GOODS, sku="123")
        )
        await goods_repo.session.commit()

        with pytest.raises(GoodsNotExists):
            await goods_repo.delete_goods(UUID("00000000-0000-0000-0000-000000000000"))
            await goods_repo.session.commit()

    async def test_delete_goods_exception_cant_delete_with_children(self, goods_repo):
        folder = await goods_repo.add_goods(
            Goods.create(name="Folder", type=GoodsType.FOLDER)
        )
        await goods_repo.add_goods(
            Goods.create(name="Goods", type=GoodsType.GOODS, sku="123", parent=folder)
        )
        await goods_repo.session.commit()

        with pytest.raises(CantDeleteWithChildren):
            await goods_repo.delete_goods(folder.id)
            await goods_repo.session.commit()

    async def test_edit_goods(self, goods_repo):
        goods = await goods_repo.add_goods(
            Goods.create(name="GoodsName", type=GoodsType.GOODS, sku="123")
        )
        await goods_repo.session.commit()

        goods_in_db: Goods = await goods_repo.session.get(Goods, goods.id)
        goods_in_db.change_name("GoodsNameChanged")
        await goods_repo.edit_goods(goods_in_db)
        await goods_repo.session.commit()

        goods_in_db = await goods_repo.session.get(Goods, goods.id)
        assert goods_in_db.name == "GoodsNameChanged"

    async def test_cant_delete_goods_with_orders(
        self, goods_repo: GoodsRepo, added_order: OrderWithRelatedData
    ):

        with pytest.raises(CantDeleteWithOrders):
            await goods_repo.delete_goods(added_order.goods.id)
            await goods_repo.session.commit()
