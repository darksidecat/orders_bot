from operator import attrgetter, itemgetter
from uuid import UUID

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.manager.protocols import ManagedDialogAdapterProto
from aiogram_dialog.widgets.input import MessageInput, TextInput
from aiogram_dialog.widgets.kbd import (
    Back,
    Button,
    Cancel,
    Next,
    Row,
    ScrollingGroup,
    Select,
)
from aiogram_dialog.widgets.managed import ManagedWidgetAdapter
from aiogram_dialog.widgets.text import Const, Format, Multi

from app.domain.goods.models.goods_type import GoodsType
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
    go_to_parent_folder,
    selected_goods_data,
)
from app.tgbot.handlers.admin.market.edit import save_selected_market_id
from app.tgbot.handlers.admin.user.common import get_user_data
from app.tgbot.handlers.dialogs.common import enable_send_mode, when_not
from app.tgbot.handlers.message_templates import format_order_message


async def get_active_goods(
    dialog_manager: DialogManager, goods_service: GoodsService, **kwargs
):
    parent_id = dialog_manager.current_context().dialog_data.get(SELECTED_GOODS)
    parent_id_as_uuid = UUID(str(parent_id)) if parent_id else None
    goods = await goods_service.get_goods_in_folder(parent_id_as_uuid, only_active=True)
    return {GOODS: goods}


async def go_to_next_level(
    query: CallbackQuery,
    select: ManagedWidgetAdapter[Select],
    manager: DialogManager,
    item_id: str,
):
    goods_service: GoodsService = manager.data.get("goods_service")

    if (await goods_service.get_goods_by_id(UUID(item_id))).type == GoodsType.GOODS:
        manager.current_context().dialog_data[SELECTED_GOODS] = item_id
        await manager.dialog().next()
    else:
        manager.current_context().dialog_data[SELECTED_GOODS] = item_id


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
                goods_id=UUID(data[SELECTED_GOODS]),
                quantity=data["quantity"],
                goods_type=GoodsType.GOODS,
            )
        ],
        creator_id=query.from_user.id,
        recipient_market_id=UUID(data[SELECTED_MARKET]),
        commentary=data["commentary"],
    )

    new_order = await order_service.add_order(order)
    data["result"] = format_order_message(new_order)
    data["new_order_id"] = str(new_order.id)

    await manager.dialog().next()
    await query.answer()


async def new_order_id_getter(dialog_manager: DialogManager, **kwargs):
    return {
        "new_order_id": dialog_manager.current_context().dialog_data.get("new_order_id")
    }


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


order_adding_process = Multi(
    Format(f"<pre>Goods:    {{{SELECTED_GOODS}.name}}</pre>", when=SELECTED_GOODS),
    Format(f"<pre>Goods:    ...</pre>", when=when_not(SELECTED_GOODS)),
    Format(f"<pre>Quantity: {{{'quantity'}}}</pre>", when="quantity"),
    Format(f"<pre>Quantity: ...</pre>", when=when_not("quantity")),
    Format(f"<pre>Market:   {{{SELECTED_MARKET}.name}}</pre>", when=SELECTED_MARKET),
    Format(f"<pre>Market:   ...</pre>", when=when_not(SELECTED_MARKET)),
    Format(f"<pre>Comments: {{{'commentary'}}}</pre>\n", when="commentary"),
    Format(f"<pre>Comments: ...</pre>\n", when=when_not("commentary")),
)


async def order_adding_process_getter(
    dialog_manager: DialogManager,
    market_service: MarketService,
    goods_service: GoodsService,
    **kwargs,
):
    data = dialog_manager.current_context().dialog_data
    market_id = data.get(SELECTED_MARKET)
    goods_id = data.get(SELECTED_GOODS)

    market = (
        await market_service.get_market_by_id(UUID(market_id)) if market_id else None
    )
    goods = await goods_service.get_goods_by_id(UUID(goods_id)) if goods_id else None
    return {
        SELECTED_GOODS: goods,
        SELECTED_MARKET: market,
        "quantity": data.get("quantity"),
        "commentary": data.get("commentary"),
    }


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
        Button(
            Const("⬅️ Back"), id="go_to_parent_folder", on_click=go_to_parent_folder
        ),
        Cancel(Const("❌ Cancel")),
        getter=[get_active_goods, get_current_goods, selected_goods_data],
        state=states.add_order.AddOrder.select_goods,
        preview_add_transitions=[Next()],
    ),
    Window(
        order_adding_process,
        Const("Input quantity"),
        TextInput(
            id="item_qt",
            type_factory=int,
            on_error=lambda q, _, __: q.answer("Invalid quantity, use digits only"),
            on_success=save_quantity,
        ),
        Row(
            Back(Const("⬅️ Back")),
            Next(Const("➡ Next️"), when="quantity"),
        ),
        Cancel(Const("❌ Cancel")),
        getter=order_adding_process_getter,
        state=states.add_order.AddOrder.input_quantity,
    ),
    Window(
        order_adding_process,
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
        Row(
            Back(Const("⬅️ Back")),
            Next(Const("➡ Next️"), when=SELECTED_MARKET),
        ),
        Cancel(Const("❌ Cancel")),
        getter=[get_active_markets, order_adding_process_getter],
        state=states.add_order.AddOrder.select_market,
    ),
    Window(
        order_adding_process,
        Const("Input commentary"),
        MessageInput(save_commentary),
        Row(
            Back(Const("⬅️ Back")),
            Next(Const("➡ Next️"), when="commentary"),
        ),
        Cancel(Const("❌ Cancel")),
        getter=order_adding_process_getter,
        state=states.add_order.AddOrder.input_comment,
    ),
    Window(
        order_adding_process,
        Const("Confirm"),
        Select(
            Format("{item[0]}"),
            id="add_yes_no",
            item_id_getter=itemgetter(1),
            items=YES_NO,
            on_click=add_order_yes_no,
        ),
        Row(Back(Const("⬅️ Back")), Cancel(Const("❌ Cancel"))),
        getter=[get_user_data, order_adding_process_getter],
        state=states.add_order.AddOrder.confirm,
        parse_mode="HTML",
        preview_add_transitions=[Next()],
    ),
    Window(
        Format("Order <pre>{new_order_id}</pre> created \n\n"),
        Format("{result}"),
        Cancel(Const("❌ Close"), on_click=enable_send_mode),
        getter=[result_getter, new_order_id_getter],
        state=states.add_order.AddOrder.result,
        parse_mode="HTML",
    ),
)
