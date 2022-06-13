from __future__ import annotations

from sqlalchemy import BIGINT, INT, TEXT, CheckConstraint, Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, ForeignKeyConstraint, Table, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.domain.goods.models.goods import Goods
from app.domain.goods.models.goods_type import GoodsType
from app.domain.market.models.market import Market
from app.domain.order.models.confirmed_status import ConfirmedStatus
from app.domain.order.models.order import Order, OrderLine, OrderMessage
from app.domain.user.models.user import TelegramUser

from .base import mapper_registry

order_line_table = Table(
    "order_line",
    mapper_registry.metadata,
    Column(
        "id",
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.uuid_generate_v4(),
    ),
    Column(
        "order_id",
        UUID(as_uuid=True),
        ForeignKey("order.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    ),
    Column(
        "goods_id",
        UUID(as_uuid=True),
        nullable=False,
    ),
    Column(
        "goods_type",
        SQLEnum(GoodsType),
        nullable=False,
    ),
    Column("quantity", BIGINT, nullable=False),
    ForeignKeyConstraint(
        ["goods_id", "goods_type"],
        ["goods.id", "goods.type"],
        name="fk_order_line_goods",
        ondelete="RESTRICT",
        onupdate="CASCADE",
    ),
    CheckConstraint("goods_type in ('GOODS')"),
)

order_table = Table(
    "order",
    mapper_registry.metadata,
    Column(
        "id",
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.uuid_generate_v4(),
    ),
    Column(
        "creator_id",
        INT,
        ForeignKey("user.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    ),
    Column("created_at", DateTime, nullable=False, server_default=func.now()),
    Column("confirmed_at", DateTime, nullable=True),
    Column("updated_at", DateTime, onupdate=func.now(), nullable=True),
    Column(
        "recipient_market_id",
        UUID(as_uuid=True),
        ForeignKey("market.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    ),
    Column("commentary", TEXT, nullable=False),
    Column(
        "confirmed",
        SQLEnum(ConfirmedStatus),
        nullable=True,
        server_default=ConfirmedStatus.NOT_PROCESSED.value,
    ),
)

order_message_table = Table(
    "order_message",
    mapper_registry.metadata,
    Column(
        "id",
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.uuid_generate_v4(),
    ),
    Column(
        "order_id",
        UUID(as_uuid=True),
        ForeignKey("order.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    ),
    Column("message_id", INT, nullable=False),
    Column("chat_id", INT, nullable=False),
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
        OrderMessage,
        order_message_table,
        properties={
            "order": relationship(
                Order,
                back_populates="order_messages",
                lazy="joined",
                uselist=False,
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
            "order_messages": relationship(
                OrderMessage,
                back_populates="order",
                lazy="joined",
            ),
        },
    )
