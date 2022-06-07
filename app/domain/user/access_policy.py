from asyncio import Protocol

from app.domain.user.dto import User


class AccessPolicy(Protocol):
    def read_access_levels(self) -> bool:
        ...

    def read_users(self) -> bool:
        ...

    def modify_user(self) -> bool:
        ...

    def read_goods(self) -> bool:
        ...

    def modify_goods(self) -> bool:
        ...

    def read_markets(self) -> bool:
        ...

    def modify_markets(self) -> bool:
        ...

    def add_order(self) -> bool:
        ...

    def read_user_self(self, user_id: int):
        ...

    def confirm_order(self) -> bool:
        ...


class AllowPolicy(AccessPolicy):
    def allow(self):
        return True

    def read_user_self(self, user_id: int):
        return True

    read_access_levels = allow
    read_users = allow
    modify_user = allow
    read_goods = allow
    modify_goods = allow

    read_markets = allow
    modify_markets = allow

    read_order = allow
    modify_order = allow
    add_order = allow
    confirm_order = allow


class UserAccessPolicy(AccessPolicy):
    def __init__(self, user: User):
        self.user = user

    def read_access_levels(self):
        return not self.user.is_blocked

    def read_users(self):
        return self.user.is_admin

    def modify_user(self):
        return self.user.is_admin

    def confirm_order(self) -> bool:
        return self.user.can_confirm_order

    read_goods = read_users
    modify_goods = modify_user

    read_markets = read_users
    modify_markets = modify_user

    read_order = read_users
    modify_order = modify_user
    add_order = read_users

    def read_user_self(self, user_id: int):
        return self.user.id == user_id
