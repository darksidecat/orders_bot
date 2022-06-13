from asyncio import Protocol
from typing import Optional
from uuid import UUID

from app.domain.order.dto import Order
from app.domain.user.dto import User


class AccessPolicy(Protocol):
    def read_access_levels(self) -> bool:
        ...

    def read_users(self) -> bool:
        ...

    def modify_users(self) -> bool:
        ...

    def read_goods(self) -> bool:
        ...

    def modify_goods(self) -> bool:
        ...

    def read_markets(self) -> bool:
        ...

    def modify_markets(self) -> bool:
        ...

    def add_orders(self) -> bool:
        ...

    def read_order(self, order: Optional[Order]) -> bool:
        ...

    def read_all_orders(self) -> bool:
        ...

    def read_user_orders(self, user_id: int) -> bool:
        ...

    def modify_orders(self) -> bool:
        ...

    def read_user_self(self, user_id: int):
        ...

    def confirm_orders(self) -> bool:
        ...


class AllowPolicy(AccessPolicy):
    def allow(self, *args, **kwargs):
        return True

    read_user_self = allow
    read_access_levels = allow
    read_users = allow
    modify_users = allow
    read_goods = allow
    modify_goods = allow

    read_markets = allow
    modify_markets = allow

    read_order = allow
    read_all_orders = allow
    read_user_orders = allow
    modify_orders = allow
    add_orders = allow
    confirm_orders = allow


class UserAccessPolicy(AccessPolicy):
    def __init__(self, user: User):
        self.user = user

    def _is_not_blocked(self):
        return not self.user.is_blocked

    def _is_admin(self):
        return self.user.is_admin

    read_users = _is_admin
    modify_users = _is_admin
    read_access_levels = _is_not_blocked
    read_goods = _is_not_blocked
    modify_goods = _is_admin

    read_markets = _is_not_blocked
    modify_markets = _is_admin

    modify_orders = _is_admin
    add_orders = _is_not_blocked

    def read_order(self, order: Optional[Order]) -> bool:
        if self.user.is_admin or self.user.can_confirm_order or not order:
            return True
        return order.creator.id == self.user.id

    def read_all_orders(self) -> bool:
        return self.user.is_admin or self.user.can_confirm_order

    def read_user_orders(self, user_id: int) -> bool:
        return self.user.id == user_id

    def read_user_self(self, user_id: int):
        return self.user.id == user_id

    def confirm_orders(self) -> bool:
        return self.user.can_confirm_order
