from asyncio import Protocol


class User(Protocol):
    id: int
    is_blocked: bool
    is_admin: bool
    can_confirm_order: bool


class UserAccessPolicy(Protocol):
    def read_users(self) -> bool:
        ...

    def modify_users(self) -> bool:
        ...

    def read_user_self(self, user_id: int):
        ...


class AllowedUserAccessPolicy(UserAccessPolicy):
    def allow(self, *args, **kwargs):
        return True

    read_user_self = allow
    read_users = allow
    modify_users = allow


class UserBasedUserAccessPolicy(UserAccessPolicy):
    def __init__(self, user: User):
        self.user = user

    def _is_not_blocked(self):
        return not self.user.is_blocked

    def _is_admin(self):
        return self.user.is_admin

    def read_user_self(self, user_id: int):
        return self.user.id == user_id

    read_users = _is_admin
    modify_users = _is_admin
