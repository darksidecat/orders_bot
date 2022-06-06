from __future__ import annotations

from datetime import datetime

from sqlalchemy import BIGINT, INT, TEXT, Column, DateTime, ForeignKey, Table, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.domain.goods.models.goods import Goods
from app.domain.market.models.market import Market
from app.domain.order.models.order import Order, OrderLine
from app.domain.user.models.user import TelegramUser

from .base import mapper_registry

order_line_table = Table(
    "order_line",
    mapper_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()),
    Column(
        "order_id",
        UUID(as_uuid=True),
        ForeignKey("order.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    ),
    Column(
        "goods_id",
        UUID(as_uuid=True),
        ForeignKey("goods.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    ),
    Column("quantity", BIGINT, nullable=False),
)

order_table = Table(
    "order",
    mapper_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()),
    Column(
        "creator_id",
        INT,
        ForeignKey("user.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    ),
    Column("created_at", DateTime, nullable=False, default=datetime.utcnow),
    Column(
        "recipient_market_id",
        UUID(as_uuid=True),
        ForeignKey("market.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    ),
    Column("commentary", TEXT, nullable=False),
)


def map_order():
    mapper_registry.map_imperatively(
        OrderLine,
        order_line_table,
        properties={
            "goods": relationship(
                Goods,
                lazy="joined",
                uselist=False,
                backref="order_lines",
            ),
        },
    )

    mapper_registry.map_imperatively(
        Order,
        order_table,
        properties={
            "creator": relationship(
                TelegramUser,
                back_populates="orders",
                lazy="joined",
                uselist=False,
                passive_deletes="all",
            ),
            "recipient_market": relationship(
                Market,
                back_populates="orders",
                lazy="joined",
                uselist=False,
                passive_deletes="all",
            ),
            "order_lines": relationship(
                OrderLine,
                backref="order",
                lazy="joined",
            ),
        },
    )
