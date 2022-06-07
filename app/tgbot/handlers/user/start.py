from aiogram import Dispatcher
from aiogram.dispatcher.fsm.state import any_state
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from app.tgbot.states import main_menu


async def user_start(m: Message, dialog_manager: DialogManager):
    await dialog_manager.start(
        state=main_menu.MainMenu.select_option, mode=StartMode.RESET_STACK
    )


def register_start(dp: Dispatcher):
    dp.message.register(user_start, any_state, commands=["start"])
