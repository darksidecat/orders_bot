from aiogram import Dispatcher
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import any_state
from aiogram.types import Message
from aiogram.utils.text_decorations import html_decoration as fmt

from app.infrastructure.database.models import TelegramUser


async def user_start(m: Message, user: TelegramUser, state: FSMContext):
    await state.clear()
    await m.reply(
        f"Hello, {fmt.quote(user.name if user else m.from_user.full_name)}!",
    )


def register_start(dp: Dispatcher):
    dp.message.register(user_start, any_state, commands=["start"])
