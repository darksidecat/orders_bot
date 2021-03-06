from aiogram import Dispatcher, Router
from aiogram_dialog import DialogRegistry

from .add_order import add_order_dialog
from .help_ import help_dialog
from .history import history_dialog
from .main_menu import main_menu_dialog


def register_user_handlers(
    dp: Dispatcher, user_router: Router, dialog_registry: DialogRegistry
):
    dialog_registry.register(main_menu_dialog, router=user_router)
    dialog_registry.register(add_order_dialog, router=user_router)
    dialog_registry.register(history_dialog, router=user_router)
    dialog_registry.register(help_dialog, router=user_router)
