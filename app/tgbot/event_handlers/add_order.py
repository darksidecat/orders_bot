import logging
from typing import Any

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.utils.text_decorations import html_decoration as fmt

from app.domain.common.events.dispatcher import EventDispatcher
from app.domain.order.models.order import OrderConfirmStatusChanged, OrderCreated
from app.domain.user.dto import User
from app.domain.user.usecases.user import UserService
from app.tgbot.handlers.chief.order_confirm import confirm_order_keyboard

logger = logging.getLogger(__name__)


async def order_created_handler(event: OrderCreated, data: dict[str, Any]):
    user_service: UserService = data["user_service"]
    bot: Bot = data["bot"]

    users: list[User] = await user_service.get_users_for_confirmation()

    message = (
        f"New order from {event.order.creator.name}\n\n"
        f"Order id:     {event.order.id}\n"
        f"Order market: {event.order.recipient_market.name}\n"
        f"Order comment:{event.order.commentary}\n\n"
    )
    for order_line in event.order.order_lines:
        message += (
            f"  Goods:      {order_line.goods.name}\n"
            f"  Quantity:   {order_line.quantity}\n"
        )
    message = fmt.pre(message)

    for user in users:
        try:
            await bot.send_message(
                chat_id=user.id,
                text=message,
                reply_markup=confirm_order_keyboard(event.order.id),
            )
        except TelegramAPIError as e:
            logger.error(e)
            continue


async def order_confirm_handler(event: OrderConfirmStatusChanged, data: dict[str, Any]):
    bot: Bot = data["bot"]

    await bot.send_message(
        chat_id=event.order.creator.id,
        text=f"Order {event.order.id} confirmed by {event.user.name}. Status: {event.order.confirmed.value}",
    )


def setup_event_handlers(event_dispatcher: EventDispatcher):
    event_dispatcher.register_notify(OrderCreated, order_created_handler)
    event_dispatcher.register_notify(OrderConfirmStatusChanged, order_confirm_handler)
