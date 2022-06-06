from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Start
from aiogram_dialog.widgets.text import Const, Text

from app.tgbot.states import admin_menu, add_order, main_menu

main_menu_dialog = Dialog(
    Window(
        Const("Select an option"),
        Start(Const("Add order"), id="add_order", state=add_order.AddOrder.select_goods),
        Start(Const("Admin menu"), id="admin_menu", state=admin_menu.AdminMenu.category),
        state=main_menu.MainMenu.select_option
    ),
)
