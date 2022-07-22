from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Cancel
from aiogram_dialog.widgets.text import Const, Format

from app.tgbot.states import help_

help_dialog = Dialog(
    Window(
        Format(
            "📚 Help\n Coming soon...",
        ),
        Cancel(Const("❌ Close")),
        state=help_.Help.show,
    ),
)
