from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const

from app.tgbot.states import history

history_dialog = Dialog(
    Window(
        Const("Select an option"),
        state=history.History.select_history_level,
    ),
)
