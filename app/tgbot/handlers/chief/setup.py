from aiogram import Dispatcher, Router

from app.tgbot.handlers.chief.order_confirm import register_handlers


def register_chief_handlers(router: Router):
    register_handlers(router=router)
