from __future__ import annotations

from sqlalchemy import TEXT, Column, Table, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.domain.market.models.market import Market
from app.infrastructure.database.models import mapper_registry

market_table = Table(
    "market",
    mapper_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()),
    Column("name", TEXT, nullable=False),
)


def map_market():
    mapper_registry.map_imperatively(
        Market,
        market_table,
        properties={
            "orders": relationship(
                "Order",
                back_populates="recipient_market",
                passive_deletes="all",
            ),
        },
    )
