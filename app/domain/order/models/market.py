from __future__ import annotations

import uuid
from uuid import UUID

import attrs
from attrs import validators

from app.domain.base.models.entity import entity


@entity
class Market:
    id: UUID = attrs.field(validator=validators.instance_of(UUID), factory=uuid.uuid4)
    name: str = attrs.field(validator=validators.instance_of(str))
    is_active: bool = attrs.field(validator=validators.instance_of(bool), default=True)
