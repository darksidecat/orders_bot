from aiogram import Dispatcher, Router
from aiogram_dialog import DialogRegistry

from ...domain.access_levels.models.access_level import LevelName
from ..filters import AccessLevelFilter
from .admin import register_admin_handlers
from .chief import register_chief_handlers
from .user import register_user_handlers


def register_handlers(dp: Dispatcher, dialog_registry: DialogRegistry):
    # admin router
    admin_router = Router()
    dp.include_router(admin_router)
    admin_router.message.filter(
        AccessLevelFilter(access_levels=LevelName.ADMINISTRATOR)
    )
    admin_router.callback_query.filter(
        AccessLevelFilter(access_levels=LevelName.ADMINISTRATOR)
    )

    register_admin_handlers(admin_router, dialog_registry)

    # chief router
    register_chief_handlers(dp)

    # user router
    allowed_access_levels = [
        LevelName.USER,
        LevelName.CONFIRMATION,
        LevelName.ADMINISTRATOR,
    ]
    admin_router.message.filter(AccessLevelFilter(access_levels=allowed_access_levels))
    admin_router.callback_query.filter(
        AccessLevelFilter(access_levels=allowed_access_levels)
    )
    user_router = Router()
    dp.include_router(user_router)
    register_user_handlers(dp, user_router, dialog_registry)
