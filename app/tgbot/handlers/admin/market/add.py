from operator import itemgetter

from aiogram.types import CallbackQuery, Message
from aiogram.utils.text_decorations import html_decoration as fmt
from aiogram_dialog import Dialog, Window
from aiogram_dialog.manager.protocols import DialogManager, ManagedDialogAdapterProto
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Back, Cancel, Next, Row, Select
from aiogram_dialog.widgets.managed import ManagedWidgetAdapter
from aiogram_dialog.widgets.text import Const, Format

from app.domain.market.dto.market import MarketCreate
from app.domain.market.usecases import MarketService
from app.tgbot import states
from app.tgbot.constants import MARKET_NAME, NO, YES_NO
from app.tgbot.handlers.dialogs.common import enable_send_mode


async def request_market_name(
    message: Message,
    dialog: ManagedDialogAdapterProto,
    manager: DialogManager,
    **kwargs,
):
    manager.current_context().dialog_data[MARKET_NAME] = message.text
    await dialog.next()


async def get_market_data(dialog_manager: DialogManager, **kwargs):
    dialog_data = dialog_manager.current_context().dialog_data

    return {
        MARKET_NAME: dialog_data.get(MARKET_NAME),
    }


async def add_market_yes_no(
    query: CallbackQuery,
    select: ManagedWidgetAdapter[Select],
    manager: DialogManager,
    item_id: str,
    **kwargs,
):
    market_service: MarketService = manager.data.get("market_service")
    data = manager.current_context().dialog_data

    if item_id == NO:
        data["result"] = "Goods adding cancelled"
        await manager.done()
        return

    market = MarketCreate(name=data[MARKET_NAME])

    market = await market_service.add_market(market)

    result = fmt.quote(
        f"Market created\n" f"id:   {market.id}\n" f"name: {market.name}\n"
    )
    data["result"] = result

    await manager.dialog().next()


async def result_getter(dialog_manager: DialogManager, **kwargs):
    return {"result": dialog_manager.current_context().dialog_data.get("result")}


add_market_dialog = Dialog(
    Window(
        Const("Input market name:"),
        MessageInput(request_market_name),
        Row(Cancel(), Next(when=MARKET_NAME)),
        state=states.market_db.AddMarket.name,
        parse_mode="HTML",
    ),
    Window(
        Format(f"Market name: {{{MARKET_NAME}}}"),
        Const("Confirm ?"),
        Select(
            Format("{item[0]}"),
            id="add_yes_no",
            item_id_getter=itemgetter(1),
            items=YES_NO,
            on_click=add_market_yes_no,
        ),
        Row(Back(), Cancel()),
        getter=get_market_data,
        state=states.market_db.AddMarket.confirm,
        parse_mode="HTML",
    ),
    Window(
        Format("{result}"),
        Cancel(Const("Close"), on_click=enable_send_mode),
        getter=result_getter,
        state=states.market_db.AddMarket.result,
        parse_mode="HTML",
    ),
)
