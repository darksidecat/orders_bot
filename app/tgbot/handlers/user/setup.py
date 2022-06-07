from aiogram import Dispatcher, Router
from aiogram_dialog import DialogRegistry

from .add_order import add_order_dialog
from .main_menu import main_menu_dialog
from .start import register_start


def register_user_handlers(
    dp: Dispatcher, user_router: Router, dialog_registry: DialogRegistry
):
    register_start(dp)
    dialog_registry.register(main_menu_dialog, router=user_router)
    dialog_registry.register(add_order_dialog, router=user_router)
