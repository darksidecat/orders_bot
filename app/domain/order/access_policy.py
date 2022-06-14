from asyncio import Protocol
from typing import Optional

from app.domain.order.dto import Order


class User(Protocol):
    id: int
    is_blocked: bool
    is_admin: bool
    can_confirm_order: bool


class OrderAccessPolicy(Protocol):
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

    def confirm_orders(self) -> bool:
        ...


class AllowedOrderAccessPolicy(OrderAccessPolicy):
    def allow(self, *args, **kwargs):
        return True

    read_order = allow
    read_all_orders = allow
    read_user_orders = allow
    modify_orders = allow
    add_orders = allow
    confirm_orders = allow


class UserBasedOrderAccessPolicy(OrderAccessPolicy):
    def __init__(self, user: User):
        self.user = user

    def _is_not_blocked(self):
        return not self.user.is_blocked

    def _is_admin(self):
        return self.user.is_admin

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

    def confirm_orders(self) -> bool:
        return self.user.can_confirm_order
