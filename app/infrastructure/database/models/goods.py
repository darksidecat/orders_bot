from sqlalchemy import BOOLEAN, TEXT, CheckConstraint, Column
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKeyConstraint, Table, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.domain.goods.models.goods import Goods
from app.domain.goods.models.goods_type import GoodsType

from .base import mapper_registry

goods_table = Table(
    "goods",
    mapper_registry.metadata,
    Column(
        "id",
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.uuid_generate_v4(),
    ),
    Column("name", TEXT, nullable=False),
    Column("type", SQLEnum(GoodsType), nullable=False),
    Column(
        "parent_id",
        UUID(as_uuid=True),
        nullable=True,
    ),
    Column("parent_type", SQLEnum(GoodsType), nullable=True),
    Column("sku", TEXT, nullable=True),
    Column("is_active", BOOLEAN, nullable=False, default=True),
    ForeignKeyConstraint(
        ["parent_id", "parent_type"],
        ["goods.id", "goods.type"],
        ondelete="RESTRICT",
        onupdate="CASCADE",
    ),
    # check constraint if type is GOODS then sku is required otherwise must be null
    CheckConstraint(
        "(type in ('GOODS') AND sku IS NOT NULL) or type in ('FOLDER')",
        name="goods_sku_not_null",
    ),
    CheckConstraint(
        "(type in ('FOLDER') AND sku IS NULL) or type in ('GOODS')",
        name="folder_sku_null",
    ),
    CheckConstraint("parent_type in ('FOLDER')", name="parent_type_is_folder"),
    UniqueConstraint("id", "type"),
)


def map_goods():
    mapper_registry.map_imperatively(
        Goods,
        goods_table,
        properties={
            "parent": relationship(
                Goods,
                remote_side=[goods_table.c.id, goods_table.c.type],
                back_populates="children",
                passive_deletes="all",
                lazy="joined",
                join_depth=1,
                uselist=False,
            ),
            "children": relationship(
                Goods,
                remote_side=[goods_table.c.parent_id, goods_table.c.parent_type],
                back_populates="parent",
                passive_deletes="all",
                lazy="joined",
                join_depth=1,
                uselist=True,
            ),
        },
    )
