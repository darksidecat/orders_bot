from aiogram import Dispatcher, F
from aiogram.dispatcher.filters.command import CommandStart
from aiogram.dispatcher.fsm.state import any_state
from aiogram.types import CallbackQuery, Message
from aiogram.utils.text_decorations import html_decoration as fmt
from aiogram_dialog import DialogManager, StartMode

from app.domain.access_levels.models.access_level import LevelName
from app.tgbot.filters import AccessLevelFilter
from app.tgbot.states import main_menu


async def user_start_unregistered_user(m: Message):
    await m.answer(
        f"You are not registered. Please, contact bot administrator. Your id is {fmt.pre(m.from_user.id)}"
    )


async def user_unregister_or_blocked(q: CallbackQuery, dialog_manager: DialogManager):
    await q.answer("You are unregistered. Please, contact bot administrator.")


async def user_start(m: Message, dialog_manager: DialogManager):
    await dialog_manager.start(
        state=main_menu.MainMenu.select_option, mode=StartMode.RESET_STACK
    )


def register_start(dp: Dispatcher):
    dp.message.register(
        user_start_unregistered_user,
        CommandStart(),
        any_state,
        AccessLevelFilter(access_levels=[]),
    )
    dp.message.register(
        user_start_unregistered_user,
        any_state,
        AccessLevelFilter(access_levels=[LevelName.BLOCKED]),
    )
    dp.callback_query.register(
        user_unregister_or_blocked, AccessLevelFilter(access_levels=[LevelName.BLOCKED])
    )
    dp.message.register(
        user_start,
        CommandStart(),
        any_state,
        AccessLevelFilter(access_levels=list(LevelName)),
    )
