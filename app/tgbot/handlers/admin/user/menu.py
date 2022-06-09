from aiogram_dialog import Dialog, StartMode, Window
from aiogram_dialog.widgets.kbd import Cancel, Start
from aiogram_dialog.widgets.text import Const

from app.tgbot.states.admin_menu import UserCategory
from app.tgbot.states.user_db import AddUser, DeleteUser, EditUser

user_menu_dialog = Dialog(
    Window(
        Const("User\n\nSelect action"),
        Start(Const("➕ Add"), id="add_user", state=AddUser.id, mode=StartMode.NORMAL),
        Start(
            Const("⚙️ Edit"),
            id="edit_user",
            state=EditUser.select_user,
            mode=StartMode.NORMAL,
        ),
        Start(
            Const("🗑️ Delete"),
            id="delete_user",
            state=DeleteUser.select_user,
            mode=StartMode.NORMAL,
        ),
        Cancel(Const("❌ Close")),
        state=UserCategory.action,
    ),
)
