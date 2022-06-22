import datetime
import math
from typing import Optional
from uuid import UUID

from aiogram.types import BufferedInputFile, CallbackQuery
from aiogram.utils.text_decorations import html_decoration as fmt
from aiogram_dialog import Dialog, DialogManager, ShowMode, Window
from aiogram_dialog.widgets.kbd import Back, Button, Cancel, Next, Row
from aiogram_dialog.widgets.text import Const, Format

from app.domain.access_levels.models.access_level import LevelName
from app.domain.order.usecases.order import OrderService
from app.domain.user.dto import User
from app.infrastructure.exporters.orders_csv import export_orders_to_csv
from app.tgbot.handlers.chief.order_confirm import confirm_order_usecase
from app.tgbot.handlers.message_templates import format_order_message
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
ORDERS_FOR_CONFIRMATION_LIMIT = 1

limit = {
    MY_ORDERS: ORDERS_ON_PAGE_LIMIT,
    ORDERS_FOR_CONFIRMATION: ORDERS_FOR_CONFIRMATION_LIMIT,
    ALL_ORDERS: ORDERS_ON_PAGE_LIMIT,
}


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

    orders = await get_orders(
        order_service=order_service,
        user=user,
        history_level=history_level,
        offset=0,
        limit=None,
    )

    csv = export_orders_to_csv(orders)
    await query.message.answer_document(
        BufferedInputFile(
            csv,
            filename=f"{history_level}-{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv",
        )
    )
    manager.show_mode = ShowMode.SEND
    await manager.dialog().show()


async def get_orders(
    order_service: OrderService,
    user: User,
    history_level: str,
    offset: int,
    limit: Optional[int],
):
    if history_level == MY_ORDERS:
        orders = await order_service.get_user_orders(
            user_id=user.id, offset=offset, limit=limit
        )
    elif history_level == ORDERS_FOR_CONFIRMATION:
        orders = await order_service.get_orders_for_confirmation(
            offset=offset, limit=limit
        )
    elif history_level == ALL_ORDERS:
        orders = await order_service.get_all_orders(offset=offset, limit=limit)
    else:
        raise ValueError(f"Unknown history level: {history_level}")

    return orders


async def get_orders_count(
    order_service: OrderService,
    user: User,
    history_level: str,
):
    if history_level == MY_ORDERS:
        orders_count = await order_service.get_user_orders_count(user_id=user.id)
    elif history_level == ORDERS_FOR_CONFIRMATION:
        orders_count = await order_service.get_orders_for_confirmation_count()
    elif history_level == ALL_ORDERS:
        orders_count = await order_service.get_all_orders_count()
    else:
        raise ValueError(f"Unknown history level: {history_level}")

    return orders_count


async def orders_getter(
    dialog_manager: DialogManager, order_service: OrderService, user: User, **kwargs
):
    history_level = dialog_manager.current_context().dialog_data["history_level"]
    offset = dialog_manager.current_context().dialog_data.setdefault("offset", 0)

    orders_count = await get_orders_count(
        order_service=order_service, user=user, history_level=history_level
    )

    if orders_count <= offset != 0:
        offset = orders_count - 1
        dialog_manager.current_context().dialog_data["offset"] = offset

    orders = await get_orders(
        order_service=order_service,
        user=user,
        history_level=history_level,
        offset=offset,
        limit=ORDERS_FOR_CONFIRMATION_LIMIT
        if history_level == ORDERS_FOR_CONFIRMATION
        else ORDERS_ON_PAGE_LIMIT,
    )

    page = offset // limit.get(history_level) + 1
    last_page = math.ceil(orders_count / limit.get(history_level))
    has_next = offset + limit.get(history_level) < orders_count

    message = f"Orders:\n\nPage: {page}/{last_page}\n\n"
    for order in orders:
        message += (
            f"Order {fmt.pre(order.id)}:\n\n{format_order_message(order)}{'-'*89}\n"
        )

    if len(orders) > 0 and history_level == ORDERS_FOR_CONFIRMATION:
        dialog_manager.current_context().dialog_data["order_id"] = str(orders[0].id)
        orders_for_confirmation = True
    else:
        orders_for_confirmation = False

    return {
        "result": message,
        "has_next": has_next,
        "has_prev": offset > 0,
        ORDERS_FOR_CONFIRMATION: orders_for_confirmation,
    }


async def previous_page(
    query: CallbackQuery, button: Button, manager: DialogManager, **kwargs
):
    history_level = manager.current_context().dialog_data["history_level"]
    manager.current_context().dialog_data["offset"] -= limit.get(history_level)


async def next_page(
    query: CallbackQuery, button: Button, manager: DialogManager, **kwargs
):
    history_level = manager.current_context().dialog_data["history_level"]
    manager.current_context().dialog_data["offset"] += limit.get(history_level)


async def reset_offset(
    query: CallbackQuery, button: Button, manager: DialogManager, **kwargs
):
    manager.current_context().dialog_data["offset"] = 0


async def save_history_level(
    query: CallbackQuery, button: Button, manager: DialogManager, **kwargs
):
    manager.current_context().dialog_data["history_level"] = button.widget_id
    await manager.dialog().next()


async def confirm_order(
    query: CallbackQuery, button: Button, manager: DialogManager, **kwargs
):
    if button.widget_id == "confirm_order":
        result = True
    else:
        result = False

    await confirm_order_usecase(
        query=query,
        order_service=manager.data["order_service"],
        user=manager.data["user"],
        bot=manager.data["bot"],
        order_id=UUID(manager.current_context().dialog_data["order_id"]),
        result=result,
        delete_reply_markup=False,
    )


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
        Format("{result}"),
        Row(
            Button(Const("✅ Confirm"), id="confirm_order", on_click=confirm_order),
            Button(Const("❌ Cancel"), id="cancel_order", on_click=confirm_order),
            when=ORDERS_FOR_CONFIRMATION,
        ),
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
