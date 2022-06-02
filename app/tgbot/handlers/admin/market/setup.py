from aiogram import Router
from aiogram_dialog import DialogRegistry

from .add import add_market_dialog
from .edit import edit_goods_dialog, market_name_dialog
from .menu import market_menu_dialog


def register_market_db_handlers(admin_router: Router, dialog_registry: DialogRegistry):
    dialog_registry.register(market_menu_dialog, router=admin_router)

    dialog_registry.register(add_market_dialog, router=admin_router)
    dialog_registry.register(edit_goods_dialog, router=admin_router)
    dialog_registry.register(market_name_dialog, router=admin_router)
