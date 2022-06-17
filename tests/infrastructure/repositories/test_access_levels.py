from app.domain.access_levels import dto
from app.domain.access_levels.models.access_level import LevelName
from app.domain.access_levels.models.helper import Levels, name_to_access_levels
from app.domain.user.models.user import TelegramUser
from app.infrastructure.database.repositories import UserRepo
from app.infrastructure.database.repositories.access_level import AccessLevelReader


class TestAccessLevelReader:
    async def test_all_access_levels(self, access_level_reader: AccessLevelReader):
        access_levels = await access_level_reader.all_access_levels()
        assert len(access_levels) == 4
        assert dto.AccessLevel.from_orm(Levels.BLOCKED.value) in access_levels
        assert dto.AccessLevel.from_orm(Levels.USER.value) in access_levels
        assert dto.AccessLevel.from_orm(Levels.ADMINISTRATOR.value) in access_levels
        assert dto.AccessLevel.from_orm(Levels.CONFIRMATION.value) in access_levels

    async def test_user_access_levels(
        self, access_level_reader: AccessLevelReader, user_repo: UserRepo
    ):
        await user_repo.add_user(
            TelegramUser(
                id=1,
                name="John",
                access_levels=name_to_access_levels(
                    [LevelName.USER, LevelName.ADMINISTRATOR]
                ),
            )
        )
        await user_repo.session.commit()

        access_levels = await access_level_reader.user_access_levels(1)
        assert len(access_levels) == 2
        assert dto.AccessLevel.from_orm(Levels.USER.value) in access_levels
        assert dto.AccessLevel.from_orm(Levels.ADMINISTRATOR.value) in access_levels
