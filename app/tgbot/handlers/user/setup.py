from aiogram import Dispatcher

from .start import register_start


def register_user_handlers(dp: Dispatcher):
    register_start(dp)
