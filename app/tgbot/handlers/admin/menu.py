from aiogram import Router
from aiogram.dispatcher.fsm.state import any_state
from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import Start
from aiogram_dialog.widgets.text import Const

from app.tgbot.states import admin_menu

admin_menu_dialog = Dialog(
    Window(
        Const("Select category"),
        Start(Const("User"), id="user_menu", state=admin_menu.UserCategory.action),
        Start(Const("Goods"), id="goods_menu", state=admin_menu.GoodsCategory.action),
        Start(
            Const("Market"), id="market_menu", state=admin_menu.MarketCategory.action
        ),
        state=admin_menu.AdminMenu.category,
    ),
)


async def admin_menu_entry(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(
        admin_menu.AdminMenu.category, mode=StartMode.RESET_STACK
    )


def register_admin_menu(dp: Router):
    dp.message.register(admin_menu_entry, any_state, commands=["admin"])
