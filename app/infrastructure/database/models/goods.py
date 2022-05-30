from sqlalchemy import BIGINT, BOOLEAN, TEXT, Column
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.domain.goods.models.goods import Goods
from app.domain.goods.models.goods_type import GoodsType

from .base import mapper_registry

goods_table = Table(
    "goods",
    mapper_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("name", TEXT, nullable=False),
    Column("type", SQLEnum(GoodsType), nullable=False),
    Column("parent_id", UUID(as_uuid=True), ForeignKey("goods.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=True),
    Column("sku", TEXT, nullable=True),
    Column("is_active", BOOLEAN, nullable=False, default=True),
)

mapper_registry.map_imperatively(
    Goods,
    goods_table,
    properties={
        "parent": relationship(
            Goods,
            remote_side=[goods_table.c.id],
            back_populates="childrens",
            lazy="selectin"),
        "childrens": relationship(Goods)
    },
)
