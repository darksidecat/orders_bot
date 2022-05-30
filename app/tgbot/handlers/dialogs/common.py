from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ShowMode


async def enable_send_mode(
    event: CallbackQuery, button, dialog_manager: DialogManager, **kwargs
):
    dialog_manager.show_mode = ShowMode.SEND


async def get_result(dialog_manager: DialogManager, **kwargs):
    return {
        "result": dialog_manager.current_context().dialog_data["result"],
    }


def when_not(key: str):
    def f(data, whenable, manager):
        return not data.get(key)

    return f
