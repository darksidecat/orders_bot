from operator import attrgetter, itemgetter
from uuid import UUID

from aiogram.types import CallbackQuery, Message
from aiogram.utils.text_decorations import html_decoration as fmt
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.manager.protocols import ManagedDialogAdapterProto
from aiogram_dialog.widgets.input import MessageInput, TextInput
from aiogram_dialog.widgets.kbd import Back, Button, Cancel, Row, ScrollingGroup, Select
from aiogram_dialog.widgets.managed import ManagedWidgetAdapter
from aiogram_dialog.widgets.text import Const, Format

from app.domain.goods.usecases.goods import GoodsService
from app.domain.market.usecases import MarketService
from app.domain.order.dto import OrderCreate, OrderLineCreate
from app.domain.order.usecases.order import OrderService
from app.tgbot import states
from app.tgbot.constants import (
    GOODS,
    MARKET,
    NO,
    SELECTED_GOODS,
    SELECTED_MARKET,
    SELECTOR_GOODS_ID,
    SELECTOR_MARKET_ID,
    YES_NO,
)
from app.tgbot.handlers.admin.goods.add import result_getter
from app.tgbot.handlers.admin.goods.edit import (
    get_current_goods,
    get_goods,
    go_to_next_level,
    go_to_parent_folder,
    selected_goods_data,
)
from app.tgbot.handlers.admin.market.edit import save_selected_market_id
from app.tgbot.handlers.admin.user.common import get_user_data
from app.tgbot.handlers.dialogs.common import enable_send_mode


async def add_new_order(
    event: CallbackQuery, button, dialog_manager: DialogManager, **kwargs
):
    order_service: OrderService = dialog_manager.data.get("order_service")
    order_lines = [
        OrderLineCreate(
            goods_id=UUID("248fcc7a-5359-4072-8f5a-241f165eb01a"), quantity=100
        )
    ]
    order_data = OrderCreate(
        order_lines=order_lines,
        creator_id=event.from_user.id,
        recipient_market_id=UUID("eec79506-c6d7-4bee-94c7-1d13479a10fe"),
        commentary="test",
    )

    await order_service.add_order(order_data)


async def get_active_goods(
    dialog_manager: DialogManager, goods_service: GoodsService, **kwargs
):
    parent_id = dialog_manager.current_context().dialog_data.get(SELECTED_GOODS)
    parent_id_as_uuid = UUID(str(parent_id)) if parent_id else None
    goods = await goods_service.get_goods_in_folder(parent_id_as_uuid, only_active=True)
    return {GOODS: goods}


async def save_quantity(
    message: Message,
    text_input: TextInput,
    dialog_manager: DialogManager,
    quantity: int,
):
    dialog_manager.current_context().dialog_data["quantity"] = quantity
    await dialog_manager.dialog().next()


async def add_order_yes_no(
    query: CallbackQuery,
    select: ManagedWidgetAdapter[Select],
    manager: DialogManager,
    item_id: str,
):
    order_service: OrderService = manager.data.get("order_service")
    data = manager.current_context().dialog_data

    if item_id == NO:
        data["result"] = "User adding cancelled"
        await manager.done()
        return

    order = OrderCreate(
        order_lines=[
            OrderLineCreate(
                goods_id=UUID(data[SELECTED_GOODS]), quantity=data["quantity"]
            )
        ],
        creator_id=query.from_user.id,
        recipient_market_id=UUID(data[SELECTED_MARKET]),
        commentary=data["commentary"],
    )

    new_order = await order_service.add_order(order)

    result = fmt.quote(f"Order created\n" f"id:           {new_order.id}\n" f"goods:\n")
    for line in new_order.order_lines:
        result += fmt.quote(
            f"    name:           {line.goods.name}\n"
            f"    quantity:     {line.quantity}\n"
        )
    data["result"] = result

    await manager.dialog().next()
    await query.answer()


async def get_active_markets(
    dialog_manager: DialogManager, market_service: MarketService, **kwargs
):
    markets = await market_service.get_all_markets(only_active=True)
    return {MARKET: markets}


async def save_commentary(
    message: Message,
    dialog: ManagedDialogAdapterProto,
    dialog_manager: DialogManager,
    **kwargs,
):
    dialog_manager.current_context().dialog_data["commentary"] = message.text
    await dialog.next()


add_order_dialog = Dialog(
    Window(
        Const("Select goods"),
        ScrollingGroup(
            Select(
                Format("{item.icon} {item.name} {item.sku_text}"),
                id=SELECTOR_GOODS_ID,
                item_id_getter=attrgetter("id"),
                items=GOODS,
                on_click=go_to_next_level,
            ),
            id="goods_scrolling",
            width=1,
            height=8,
        ),
        Button(Const("Back"), id="go_to_parent_folder", on_click=go_to_parent_folder),
        Cancel(),
        getter=[get_active_goods, get_current_goods, selected_goods_data],
        state=states.add_order.AddOrder.select_goods,
    ),
    Window(
        Const("Input quantity"),
        TextInput(
            id="item_qt",
            type_factory=int,
            on_error=lambda q, _, __: q.answer("Invalid quantity, use digits only"),
            on_success=save_quantity,
        ),
        state=states.add_order.AddOrder.input_quantity,
    ),
    Window(
        Const("Select market:"),
        ScrollingGroup(
            Select(
                Format("{item.name}"),
                id=SELECTOR_MARKET_ID,
                item_id_getter=attrgetter("id"),
                items=MARKET,
                on_click=save_selected_market_id,
            ),
            id="market_scrolling",
            width=1,
            height=8,
        ),
        Cancel(),
        getter=get_active_markets,
        state=states.add_order.AddOrder.select_market,
    ),
    Window(
        Const("Input commentary"),
        MessageInput(save_commentary),
        state=states.add_order.AddOrder.input_comment,
    ),
    Window(
        Const("Confirm"),
        Select(
            Format("{item[0]}"),
            id="add_yes_no",
            item_id_getter=itemgetter(1),
            items=YES_NO,
            on_click=add_order_yes_no,
        ),
        Row(Back(), Cancel()),
        getter=get_user_data,
        state=states.add_order.AddOrder.confirm,
        parse_mode="HTML",
    ),
    Window(
        Format("{result}"),
        Cancel(Const("Close"), on_click=enable_send_mode),
        getter=[result_getter],
        state=states.add_order.AddOrder.result,
        parse_mode="HTML",
    ),
)
