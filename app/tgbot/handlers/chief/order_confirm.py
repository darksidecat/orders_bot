from uuid import UUID

from aiogram import Router
from aiogram.dispatcher.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from app.domain.order.usecases.order import OrderService
from app.domain.user.dto import User


class OrderConfirm(CallbackData, prefix="order_confirm"):
    order_id: UUID
    result: bool


def confirm_order_keyboard(order_id: UUID):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Confirm",
                    callback_data=OrderConfirm(order_id=order_id, result=True).pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text="Cancel",
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
):
    await order_service.change_confirm_status(
        callback_data.order_id, confirmed=callback_data.result, confirmed_by=user
    )
    if callback_data.result:
        await query.answer("Order confirmed")
    else:
        await query.answer("Order canceled")
    await query.message.edit_reply_markup(reply_markup=None)


def register_handlers(router: Router):
    router.callback_query.register(confirm_order, OrderConfirm.filter())
