from aiogram import Router
from aiogram_dialog import DialogRegistry

from .add import add_user_dialog
from .delete import delete_user_dialog
from .edit import (
    edit_user_dialog,
    user_access_levels_dialog,
    user_id_dialog,
    user_name_dialog,
)
from .menu import user_menu_dialog


def register_user_db_handlers(admin_router: Router, dialog_registry: DialogRegistry):
    dialog_registry.register(user_menu_dialog, router=admin_router)

    dialog_registry.register(add_user_dialog, router=admin_router)

    dialog_registry.register(edit_user_dialog, router=admin_router)
    dialog_registry.register(user_id_dialog, router=admin_router)
    dialog_registry.register(user_name_dialog, router=admin_router)
    dialog_registry.register(user_access_levels_dialog, router=admin_router)

    dialog_registry.register(delete_user_dialog, router=admin_router)
