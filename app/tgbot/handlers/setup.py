from aiogram import Dispatcher, Router
from aiogram_dialog import DialogRegistry

from .admin import register_admin_handlers
from .chief import register_chief_handlers
from .user import register_user_handlers


def register_handlers(
    dp: Dispatcher, admin_router: Router, dialog_registry: DialogRegistry
):

    register_admin_handlers(admin_router, dialog_registry)
    register_chief_handlers(dp)
    register_user_handlers(dp, dialog_registry)
