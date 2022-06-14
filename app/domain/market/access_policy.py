from asyncio import Protocol


class User(Protocol):
    id: int
    is_blocked: bool
    is_admin: bool
    can_confirm_order: bool


class MarketAccessPolicy1(Protocol):
    def read_markets(self) -> bool:
        ...

    def modify_markets(self) -> bool:
        ...


class AllowedMarketAccessPolicy(MarketAccessPolicy1):
    def allow(self, *args, **kwargs):
        return True

    read_markets = allow
    modify_markets = allow


class UserBasedMarketAccessPolicy(MarketAccessPolicy1):
    def __init__(self, user: User):
        self.user = user

    def _is_not_blocked(self):
        return not self.user.is_blocked

    def _is_admin(self):
        return self.user.is_admin

    read_markets = _is_not_blocked
    modify_markets = _is_admin
