from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Cancel
from aiogram_dialog.widgets.text import Const, Format

from app.tgbot.states import help_

help_dialog = Dialog(
    Window(
        Format(
            "<pre>📚 Help</pre>\n",
        ),
        Cancel(Const("❌ Close")),
        state=help_.Help.show,
    ),
)
