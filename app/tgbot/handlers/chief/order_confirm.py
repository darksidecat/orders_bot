import logging
from uuid import UUID

from aiogram import Bot, Router
from aiogram.dispatcher.filters.callback_data import CallbackData
from aiogram.exceptions import TelegramAPIError
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from app.domain.order.exceptions.order import OrderAlreadyConfirmed
from app.domain.order.usecases.order import OrderService
from app.domain.order.value_objects.confirmed_status import ConfirmedStatus
from app.domain.user.dto import User
from app.tgbot.handlers.message_templates import format_order_message

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


async def confirm_order_usecase(
    query: CallbackQuery,
    order_service: OrderService,
    user: User,
    bot: Bot,
    order_id: UUID,
    result: bool,
    delete_reply_markup: bool,
):
    confirmed_status = ConfirmedStatus.YES if result else ConfirmedStatus.NO

    try:
        await order_service.change_confirm_status(
            order_id, confirmed_status=confirmed_status, confirmed_by=user
        )
    except OrderAlreadyConfirmed:
        await query.answer("Order already confirmed")
        try:
            if delete_reply_markup:
                await query.message.edit_reply_markup(reply_markup=None)
        except TelegramAPIError:
            #  If reply_markup is already deleted
            pass
    if result:
        await query.answer("Order confirmed")
    else:
        await query.answer("Order canceled")
    order = await order_service.get_order_by_id(order_id)

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


async def confirm_order(
    query: CallbackQuery,
    callback_data: OrderConfirm,
    order_service: OrderService,
    user: User,
    bot: Bot,
):
    await confirm_order_usecase(
        query=query,
        order_service=order_service,
        user=user,
        bot=bot,
        order_id=callback_data.order_id,
        result=callback_data.result,
        delete_reply_markup=True,
    )


def register_handlers(router: Router):
    router.callback_query.register(confirm_order, OrderConfirm.filter())
