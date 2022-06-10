import logging
from uuid import UUID

from aiogram import Bot, Router
from aiogram.dispatcher.filters.callback_data import CallbackData
from aiogram.exceptions import TelegramAPIError
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from app.domain.order.exceptions.order import OrderAlreadyConfirmed
from app.domain.order.usecases.order import OrderService
from app.domain.user.dto import User
from app.tgbot.handlers.user.add_order import format_order_message

logger = logging.getLogger(__name__)


class OrderConfirm(CallbackData, prefix="order_confirm"):
    order_id: UUID
    result: bool


def confirm_order_keyboard(order_id: UUID):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Confirm",
                    callback_data=OrderConfirm(order_id=order_id, result=True).pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Cancel",
                    callback_data=OrderConfirm(order_id=order_id, result=False).pack(),
                )
            ],
        ]
    )
    return keyboard


async def confirm_order(
    query: CallbackQuery,
    callback_data: OrderConfirm,
    order_service: OrderService,
    user: User,
    bot: Bot,
):
    try:
        await order_service.change_confirm_status(
            callback_data.order_id, confirmed=callback_data.result, confirmed_by=user
        )
    except OrderAlreadyConfirmed:
        await query.answer("Order already confirmed")
    if callback_data.result:
        await query.answer("Order confirmed")
    else:
        await query.answer("Order canceled")
    order = await order_service.get_order_by_id(callback_data.order_id, has_access=True)

    for message in order.order_messages:
        try:
            await bot.edit_message_text(
                text=format_order_message(order),
                chat_id=message.chat_id,
                message_id=message.message_id,
                reply_markup=None,
            )
        except TelegramAPIError as e:
            logger.error(e)
            continue


def register_handlers(router: Router):
    router.callback_query.register(confirm_order, OrderConfirm.filter())
