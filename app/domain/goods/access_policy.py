from asyncio import Protocol


class User(Protocol):
    id: int
    is_blocked: bool
    is_admin: bool
    can_confirm_order: bool


class GoodsAccessPolicy(Protocol):
    def read_goods(self) -> bool:
        ...

    def modify_goods(self) -> bool:
        ...


class AllowedGoodsAccessPolicy(GoodsAccessPolicy):
    def allow(self, *args, **kwargs):
        return True

    read_goods = allow
    modify_goods = allow


class UserBasedGoodsAccessPolicy(GoodsAccessPolicy):
    def __init__(self, user: User):
        self.user = user

    def _is_not_blocked(self):
        return not self.user.is_blocked

    def _is_admin(self):
        return self.user.is_admin

    read_goods = _is_not_blocked
    modify_goods = _is_admin
