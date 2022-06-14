import logging
from typing import Any

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.utils.text_decorations import html_decoration as fmt

from app.domain.base.events.dispatcher import EventDispatcher
from app.domain.order.access_policy import AllowedOrderAccessPolicy
from app.domain.order.dto.order import OrderMessageCreate
from app.domain.order.models.order import OrderConfirmStatusChanged, OrderCreated
from app.domain.order.usecases.order import OrderService
from app.domain.user.access_policy import AllowedUserAccessPolicy
from app.domain.user.dto import User
from app.domain.user.usecases.user import UserService
from app.tgbot.handlers.chief.order_confirm import confirm_order_keyboard
from app.tgbot.handlers.user.common import format_order_message

logger = logging.getLogger(__name__)


async def order_created_handler(event: OrderCreated, data: dict[str, Any]):
    event_dispatcher = data.get("event_dispatcher")
    uow = data.get("uow")
    bot: Bot = data["bot"]

    user_service = UserService(
        access_policy=AllowedUserAccessPolicy(),
        event_dispatcher=event_dispatcher,
        uow=uow,
    )
    order_service = OrderService(
        access_policy=AllowedOrderAccessPolicy(),
        event_dispatcher=event_dispatcher,
        uow=uow,
    )

    users: list[User] = await user_service.get_users_for_confirmation()

    message_text = (
        f"New order {fmt.pre(event.order.id)} from {event.order.creator.name}\n\n"
        + format_order_message(event.order)
    )

    sent_messages = []
    for user in users:
        try:
            message = await bot.send_message(
                chat_id=user.id,
                text=message_text,
                reply_markup=confirm_order_keyboard(event.order.id),
            )
            sent_messages.append(
                OrderMessageCreate(
                    message_id=message.message_id, chat_id=message.chat.id
                )
            )
        except TelegramAPIError as e:
            logger.error(e)
            continue

    await order_service.add_order_messages(event.order.id, sent_messages)


async def order_confirm_handler(event: OrderConfirmStatusChanged, data: dict[str, Any]):
    bot: Bot = data["bot"]

    await bot.send_message(
        chat_id=event.order.creator.id,
        text=f"Order {fmt.pre(event.order.id)} confirmed by {event.user.name}\n\n"
        + format_order_message(event.order),
    )


def setup_event_handlers(event_dispatcher: EventDispatcher):
    event_dispatcher.register_notify(OrderCreated, order_created_handler)
    event_dispatcher.register_notify(OrderConfirmStatusChanged, order_confirm_handler)
