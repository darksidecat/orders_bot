from aiogram import Router
from aiogram_dialog import DialogRegistry

from .add import add_goods_dialog
from .edit import (
    edit_goods_dialog,
    goods_name_dialog,
    goods_sku_dialog,
    selected_goods_dialog,
)
from .menu import goods_menu_dialog


def register_goods_db_handlers(admin_router: Router, dialog_registry: DialogRegistry):
    dialog_registry.register(goods_menu_dialog, router=admin_router)

    dialog_registry.register(add_goods_dialog, router=admin_router)
    dialog_registry.register(edit_goods_dialog, router=admin_router)
    dialog_registry.register(selected_goods_dialog, router=admin_router)
    dialog_registry.register(goods_name_dialog, router=admin_router)
    dialog_registry.register(goods_sku_dialog, router=admin_router)
