from operator import attrgetter
from uuid import UUID

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.manager.protocols import ManagedDialogAdapterProto
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import (
    Back,
    Button,
    Cancel,
    ScrollingGroup,
    Select,
    Start,
)
from aiogram_dialog.widgets.managed import ManagedWidgetAdapter
from aiogram_dialog.widgets.text import Const, Format

from app.domain.market.dto import MarketPatch
from app.domain.market.exceptions.market import CantDeleteWithOrders
from app.domain.market.usecases import MarketService
from app.tgbot import states
from app.tgbot.constants import MARKET, SELECTED_MARKET, SELECTOR_MARKET_ID
from app.tgbot.handlers.admin.user.common import copy_start_data_to_context


async def add_new_market(
    query: CallbackQuery, button: Button, manager: DialogManager, **kwargs
):
    data_for_copy = {
        SELECTED_MARKET: manager.current_context().dialog_data.get(SELECTED_MARKET)
    }
    await manager.start(states.market_db.AddMarket.name, data=data_for_copy)


async def get_markets(
    dialog_manager: DialogManager, market_service: MarketService, **kwargs
):
    markets = await market_service.get_all_markets(only_active=True)
    return {MARKET: markets}


async def save_selected_market_id(
    query: CallbackQuery,
    dialog: ManagedWidgetAdapter[Select],
    manager: DialogManager,
    item_id: str,
):
    manager.current_context().dialog_data[SELECTED_MARKET] = item_id
    await manager.dialog().next()


async def start_edit_market_name_dialog(
    query: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    selected_market = manager.current_context().dialog_data.get(SELECTED_MARKET)
    data_for_copy = {SELECTED_MARKET: selected_market}
    await manager.start(states.market_db.EditMarketName.request, data=data_for_copy)


async def request_name(
    message: Message, dialog: ManagedDialogAdapterProto, manager: DialogManager
):
    service: MarketService = manager.data.get("market_service")
    selected_market = UUID(manager.current_context().dialog_data.get(SELECTED_MARKET))
    await service.patch_market(MarketPatch(id=selected_market, name=message.text))
    await manager.done()


async def delete_market(
    query: CallbackQuery, button: Button, manager: DialogManager, **kwargs
):
    goods_service: MarketService = manager.data.get("market_service")

    parent_id = manager.current_context().dialog_data.get(SELECTED_MARKET)
    try:
        await goods_service.delete_market(UUID(parent_id))
    except CantDeleteWithOrders:
        await query.answer("Can't delete market with orders")
        return

    await query.answer("Goods deleted")
    await manager.dialog().switch_to(states.market_db.EditMarket.select_market)


async def get_selected_market(
    dialog_manager: DialogManager, market_service: MarketService, **kwargs
):
    market = dialog_manager.current_context().dialog_data.get(SELECTED_MARKET)
    print(market)
    market = await market_service.get_market_by_id(UUID(market))
    print(market)
    return {MARKET: market}


market_name_dialog = Dialog(
    Window(
        Const("Send new market name"),
        MessageInput(request_name),
        state=states.market_db.EditMarketName.request,
    ),
    on_start=copy_start_data_to_context,
)

edit_goods_dialog = Dialog(
    Window(
        Const("Select market for editing:"),
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
        Button(Const("➕ Add new"), on_click=add_new_market, id="add_new_market"),
        Cancel(Const("❌ Close")),
        getter=get_markets,
        state=states.market_db.EditMarket.select_market,
    ),
    Window(
        Format(f"Selected market: {{{MARKET}.name}}"),
        Const("Select option"),
        Button(
            Const("Edit name"), on_click=start_edit_market_name_dialog, id="edit_name"
        ),
        Button(Const("🗑️ Delete"), on_click=delete_market, id="delete_goods"),
        Back(Const("🔙 Back")),
        Cancel(Const("❌ Close")),
        getter=get_selected_market,
        state=states.market_db.EditMarket.select_action,
    ),
)
