from sqlalchemy import BOOLEAN, TEXT, Column, Computed, ForeignKeyConstraint
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Table, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.domain.goods.models.goods import Goods
from app.domain.goods.models.goods_type import GoodsType

from .base import mapper_registry


nomenclature_table = Table(
    "nomenclature",
    mapper_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=func.uuid_generate_v4()),
    Column("type", SQLEnum(GoodsType), nullable=False),
    Column("name", TEXT, nullable=False),
    UniqueConstraint("id", "type", name="uq_nomenclature_id_type"),
)

folder_table = Table(
    "folder",
    mapper_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("type", SQLEnum(GoodsType), Computed("FOLDER"), nullable=False),
    Column("parent_id", UUID(as_uuid=True), ForeignKey("folder.id")),
    ForeignKeyConstraint(
        ["id", "type"],
        ["nomenclature.id", "nomenclature.type"],
        name="fk_folder_nomenclature",
        ondelete="CASCADE",
        onupdate="CASCADE",
    ),
)

goods_table = Table(
    "goods",
    mapper_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("type", SQLEnum(GoodsType), Computed("GOODS"), nullable=False),
    Column("parent_id", UUID(as_uuid=True), ForeignKey("folder.id")),
    Column("sku", TEXT, nullable=False),
    ForeignKeyConstraint(
        ["id", "type"],
        ["nomenclature.id", "nomenclature.type"],
        name="fk_folder_nomenclature",
        ondelete="CASCADE",
        onupdate="CASCADE",
    ),
)

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
        ForeignKey("goods.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=True,
    ),
    Column("sku", TEXT, nullable=True),
    Column("is_active", BOOLEAN, nullable=False, default=True),
    UniqueConstraint("id", "type", name="uq_goods_id_type"),
)


def map_goods():
    mapper_registry.map_imperatively(
        Goods,
        goods_table,
        properties={
            "parent": relationship(
                Goods,
                remote_side=[goods_table.c.id],
                passive_deletes="all",
                back_populates="childrens",
                lazy="selectin",
            ),
            "childrens": relationship(
                Goods,
                remote_side=[goods_table.c.parent_id],
                lazy="selectin",
                passive_deletes="all",
            ),
        },
    )
