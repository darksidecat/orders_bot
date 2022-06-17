from __future__ import annotations

from sqlalchemy import BIGINT, INT, TEXT, CheckConstraint, Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, ForeignKeyConstraint, Table, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.domain.order import models
from app.domain.order.models.goods import GoodsType
from app.domain.order.models.order import Order, OrderLine, OrderMessage
from app.domain.order.value_objects.confirmed_status import ConfirmedStatus

from .base import mapper_registry
from .goods import goods_table
from .market import market_table
from .user import access_level_table, user_access_levels, user_table

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
                models.goods.Goods,
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
                models.user.TelegramUser,
                back_populates="orders",
                lazy="joined",
                innerjoin=True,
                uselist=False,
                passive_deletes="all",
            ),
            "recipient_market": relationship(
                models.market.Market,
                back_populates="orders",
                lazy="joined",
                innerjoin=True,
                uselist=False,
                passive_deletes="all",
            ),
            "order_lines": relationship(
                OrderLine,
                backref="order",
                lazy="joined",
                passive_deletes="all",
            ),
            "order_messages": relationship(
                OrderMessage,
                back_populates="order",
                lazy="joined",
            ),
        },
    )

    mapper_registry.map_imperatively(
        models.goods.Goods,
        goods_table,
        properties={
            "parent": relationship(
                models.goods.Goods,
                remote_side=[goods_table.c.id, goods_table.c.type],
                back_populates="children",
                lazy="joined",
                join_depth=1,
                uselist=False,
                viewonly=True,
            ),
            "children": relationship(
                models.goods.Goods,
                remote_side=[goods_table.c.parent_id, goods_table.c.parent_type],
                back_populates="parent",
                lazy="joined",
                join_depth=1,
                uselist=True,
                viewonly=True,
            ),
        },
    )

    mapper_registry.map_imperatively(
        models.market.Market,
        market_table,
        properties={
            "orders": relationship(
                "Order",
                back_populates="recipient_market",
                viewonly=True,
            ),
        },
    )
    mapper_registry.map_imperatively(
        models.user.TelegramUser,
        user_table,
        properties={
            "access_levels": relationship(
                models.user.AccessLevel,
                secondary=user_access_levels,
                back_populates="users",
                lazy="selectin",
                viewonly=True,
            ),
            "orders": relationship(
                "Order",
                back_populates="creator",
                lazy="noload",
                viewonly=True,
            ),
        },
    )
    mapper_registry.map_imperatively(
        models.user.AccessLevel,
        access_level_table,
        properties={
            "users": relationship(
                models.user.TelegramUser,
                secondary=user_access_levels,
                back_populates="access_levels",
                viewonly=True,
            )
        },
    )
