from app.domain.user.models.user import TelegramUser


class AccessLevelsAccessPolicy:
    def __init__(self, user: TelegramUser):
        self.user = user

    def read_access_levels(self):
        return not self.user.is_blocked
