from operator import attrgetter
from uuid import UUID

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.manager.protocols import ManagedDialogAdapterProto
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Cancel, ScrollingGroup, Select, Start
from aiogram_dialog.widgets.managed import ManagedWidgetAdapter
from aiogram_dialog.widgets.text import Const, Format

from app.domain.market.dto import MarketPatch
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
    markets = await market_service.get_all_markets()
    return {MARKET: markets}


async def start_edit_market_name_dialog(
    query: CallbackQuery,
    select: ManagedWidgetAdapter[Select],
    manager: DialogManager,
    item_id: str,
):
    data_for_copy = {SELECTED_MARKET: item_id}
    await manager.start(states.market_db.EditMarketName.request, data=data_for_copy)


async def request_name(
    message: Message, dialog: ManagedDialogAdapterProto, manager: DialogManager
):
    service: MarketService = manager.data.get("market_service")
    selected_market = UUID(manager.current_context().dialog_data.get(SELECTED_MARKET))
    await service.patch_market(MarketPatch(id=selected_market, name=message.text))
    await manager.done()


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
                on_click=start_edit_market_name_dialog,
            ),
            id="market_scrolling",
            width=1,
            height=8,
        ),
        Button(Const("Add new"), on_click=add_new_market, id="add_new_market"),
        Cancel(),
        getter=get_markets,
        state=states.market_db.EditMarket.select_goods,
    ),
)
