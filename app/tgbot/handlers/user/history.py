import math
from typing import Optional

from aiogram.types import BufferedInputFile, CallbackQuery, InputFile
from aiogram.utils.text_decorations import html_decoration as fmt
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Back, Button, Cancel, Next, Row
from aiogram_dialog.widgets.text import Const, Format

from app.domain.access_levels.models.access_level import LevelName
from app.domain.order.usecases.order import OrderService
from app.domain.user.dto import User
from app.infrastructure.exporters.orders_csv import export_orders_to_csv
from app.tgbot.handlers.user.common import format_order_message
from app.tgbot.states import history

my_orders_access_levels = [
    LevelName.USER,
    LevelName.ADMINISTRATOR,
    LevelName.CONFIRMATION,
]
order_for_confirmation_access_levels = [LevelName.CONFIRMATION]
all_orders_access_levels = [LevelName.ADMINISTRATOR, LevelName.CONFIRMATION]

MY_ORDERS = "my_orders"
ORDERS_FOR_CONFIRMATION = "orders_for_confirmation"
ALL_ORDERS = "all_orders"

ORDERS_ON_PAGE_LIMIT = 2


async def history_access_getter(dialog_manager: DialogManager, user: User, **kwargs):
    access_levels = {}
    for level_name in my_orders_access_levels:
        if level_name in (level.name for level in user.access_levels):
            access_levels[MY_ORDERS] = True
    for level_name in order_for_confirmation_access_levels:
        if level_name in (level.name for level in user.access_levels):
            access_levels[ORDERS_FOR_CONFIRMATION] = True
    for level_name in all_orders_access_levels:
        if level_name in (level.name for level in user.access_levels):
            access_levels[ALL_ORDERS] = True
    return access_levels


async def import_orders_csv(
    query: CallbackQuery, button: Button, manager: DialogManager, **kwargs
):
    history_level = manager.current_context().dialog_data["history_level"]
    order_service = manager.data["order_service"]
    user = manager.data["user"]

    orders, _ = await get_orders(
        order_service=order_service,
        user=user,
        history_level=history_level,
        offset=0,
        limit=None,
    )

    csv = export_orders_to_csv(orders)
    await query.message.answer_document(BufferedInputFile(csv, filename="orders.csv"))


async def get_orders(
    order_service: OrderService,
    user: User,
    history_level: str,
    offset: int,
    limit: Optional[int] = ORDERS_ON_PAGE_LIMIT,
):
    if history_level == MY_ORDERS:
        orders = await order_service.get_user_orders(
            user_id=user.id, offset=offset, limit=limit
        )
        orders_count = await order_service.get_user_orders_count(user_id=user.id)
    elif history_level == ORDERS_FOR_CONFIRMATION:
        orders = await order_service.get_orders_for_confirmation(
            offset=offset, limit=limit
        )
        orders_count = await order_service.get_orders_for_confirmation_count()
    elif history_level == ALL_ORDERS:
        orders = await order_service.get_all_orders(offset=offset, limit=limit)
        orders_count = await order_service.get_all_orders_count()
    else:
        raise ValueError(f"Unknown history level: {history_level}")

    return orders, orders_count


async def orders_getter(
    dialog_manager: DialogManager, order_service: OrderService, user: User, **kwargs
):
    history_level = dialog_manager.current_context().dialog_data["history_level"]
    offset = dialog_manager.current_context().dialog_data.setdefault("offset", 0)

    orders, orders_count = await get_orders(
        order_service=order_service,
        user=user,
        history_level=history_level,
        offset=offset,
    )

    message = f"Orders:\n\nPage: {offset // ORDERS_ON_PAGE_LIMIT + 1}/{math.ceil(orders_count / ORDERS_ON_PAGE_LIMIT)}\n\n"
    for order in orders:
        message += (
            f"Order {fmt.pre(order.id)}:\n\n{format_order_message(order)}{'-'*89}\n"
        )

    return {
        "result": message,
        "has_next": offset + ORDERS_ON_PAGE_LIMIT < orders_count,
        "has_prev": offset > 0,
    }


async def previous_page(
    query: CallbackQuery, button: Button, manager: DialogManager, **kwargs
):
    manager.current_context().dialog_data["offset"] -= ORDERS_ON_PAGE_LIMIT


async def next_page(
    query: CallbackQuery, button: Button, manager: DialogManager, **kwargs
):
    manager.current_context().dialog_data["offset"] += ORDERS_ON_PAGE_LIMIT


async def reset_offset(
    query: CallbackQuery, button: Button, manager: DialogManager, **kwargs
):
    manager.current_context().dialog_data["offset"] = 0


async def save_history_level(
    query: CallbackQuery, button: Button, manager: DialogManager, **kwargs
):
    manager.current_context().dialog_data["history_level"] = button.widget_id
    await manager.dialog().next()


history_dialog = Dialog(
    Window(
        Const("Select an option"),
        Button(
            Const("My orders  history"),
            id=MY_ORDERS,
            on_click=save_history_level,
            when=MY_ORDERS,
        ),
        Button(
            Const("Orders for my confirmation"),
            id=ORDERS_FOR_CONFIRMATION,
            on_click=save_history_level,
            when=ORDERS_FOR_CONFIRMATION,
        ),
        Button(
            Const("All orders"),
            id=ALL_ORDERS,
            on_click=save_history_level,
            when=ALL_ORDERS,
        ),
        Cancel(Const("❌ Close")),
        state=history.History.select_history_level,
        getter=[history_access_getter],
        preview_add_transitions=[Next()],
    ),
    Window(
        Const("Select an option"),
        Format("{result}"),
        # add 2 buttons for previous and next page
        Row(
            Button(
                Const("⬅️ Previous page"),
                id="previous_page",
                on_click=previous_page,
                when="has_prev",
            ),
            Button(
                Const("➡️ Next page"),
                id="next_page",
                on_click=next_page,
                when="has_next",
            ),
        ),
        Button(
            Const("💾 Import data"), id="import_orders_csv", on_click=import_orders_csv
        ),
        Back(Const("↩️ Back to history"), on_click=reset_offset),
        Cancel(Const("❌ Close")),
        state=history.History.show,
        getter=[orders_getter],
    ),
)
