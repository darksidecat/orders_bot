from app.domain.user.dto import User


class UserAccessPolicy:
    def __init__(self, user: User):
        self.user = user

    def read_access_levels(self):
        return not self.user.is_blocked

    def read_users(self, internal: bool = False):
        if internal:
            return True
        elif self.user.is_blocked:
            return False
        else:
            return self.user.is_admin

    def modify_user(self):
        return self.user.is_admin

    read_goods = read_users
    modify_goods = modify_user

    read_markets = read_users
    modify_markets = modify_user

    def read_user_self(self, user_id: int):
        return self.user.id == user_id
