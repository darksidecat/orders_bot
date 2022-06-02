from aiogram import Router
from aiogram_dialog import DialogRegistry

from app.domain.access_levels.dto.access_level import LevelName

from ...filters import AccessLevelFilter
from .goods import register_goods_db_handlers
from .market.setup import register_market_db_handlers
from .menu import admin_menu_dialog, register_admin_menu
from .user import register_user_db_handlers


def register_admin_handlers(admin_router: Router, dialog_registry: DialogRegistry):
    admin_router.message.filter(
        AccessLevelFilter(access_levels=LevelName.ADMINISTRATOR)
    )
    admin_router.callback_query.filter(
        AccessLevelFilter(access_levels=LevelName.ADMINISTRATOR)
    )

    register_admin_menu(admin_router)
    dialog_registry.register(admin_menu_dialog, router=admin_router)

    register_user_db_handlers(admin_router, dialog_registry)
    register_goods_db_handlers(admin_router, dialog_registry)
    register_market_db_handlers(admin_router, dialog_registry)
