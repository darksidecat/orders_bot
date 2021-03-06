from asyncio import Protocol


class User(Protocol):
    id: int
    is_blocked: bool
    is_admin: bool
    can_confirm_order: bool


class AccessLevelsAccessPolicy(Protocol):
    def read_access_levels(self) -> bool:
        ...


class AllowedAccessLevelsPolicy(AccessLevelsAccessPolicy):
    def allow(self, *args, **kwargs):
        return True

    read_access_levels = allow


class UserBasedAccessLevelsAccessPolicy(AccessLevelsAccessPolicy):
    def __init__(self, user: User):
        self.user = user

    def _is_not_blocked(self):
        return not self.user.is_blocked

    def _is_admin(self):
        return self.user.is_admin

    read_access_levels = _is_not_blocked
