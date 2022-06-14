from aiogram import F
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Start
from aiogram_dialog.widgets.text import Const

from app.domain.user.dto import User
from app.tgbot.states import add_order, admin_menu, help_, history, main_menu


async def get_user(dialog_manager: DialogManager, user: User, **kwargs):
    return {"user": user}


main_menu_dialog = Dialog(
    Window(
        Const("Select an option"),
        Start(
            Const("➕ Add order"), id="add_order", state=add_order.AddOrder.select_goods
        ),
        Start(
            Const("📜 History"), id="history", state=history.History.select_history_level
        ),
        Start(
            Const("🛠 Admin menu"),
            id="admin_menu",
            state=admin_menu.AdminMenu.category,
            when=F["user"].is_admin,
        ),
        Start(Const("❓ Help"), id="help", state=help_.Help.show),
        getter=get_user,
        state=main_menu.MainMenu.select_option,
    ),
)
