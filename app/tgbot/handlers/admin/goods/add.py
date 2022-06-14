from operator import itemgetter

from aiogram.types import CallbackQuery, Message
from aiogram.utils.text_decorations import html_decoration as fmt
from aiogram_dialog import Dialog, Window
from aiogram_dialog.manager.protocols import DialogManager, ManagedDialogAdapterProto
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Back, Button, Cancel, Next, Row, Select
from aiogram_dialog.widgets.managed import ManagedWidgetAdapter
from aiogram_dialog.widgets.text import Const, Format

from app.domain.goods.dto.goods import GoodsCreate
from app.domain.goods.models.goods_type import GoodsType
from app.domain.goods.usecases.goods import GoodsService
from app.tgbot import states
from app.tgbot.constants import (
    GOODS_NAME,
    GOODS_SKU,
    GOODS_TYPE,
    NO,
    SELECTED_GOODS,
    YES_NO,
)
from app.tgbot.handlers.admin.goods.common import get_goods_data, goods_adding_process
from app.tgbot.handlers.admin.user.common import copy_start_data_to_context
from app.tgbot.handlers.dialogs.common import enable_send_mode
from app.tgbot.states.goods_db import AddGoods


async def request_goods_name(
    message: Message,
    dialog: ManagedDialogAdapterProto,
    manager: DialogManager,
    **kwargs,
):
    manager.current_context().dialog_data[GOODS_NAME] = message.text
    await dialog.next()


async def save_goods_type(
    query: CallbackQuery,
    select: ManagedWidgetAdapter[Select],
    manager: DialogManager,
    item_id: str,
    **kwargs,
):
    manager.current_context().dialog_data[GOODS_TYPE] = item_id
    if item_id == GoodsType.FOLDER.value:
        await manager.dialog().switch_to(AddGoods.confirm)
    else:
        await manager.dialog().next()


async def request_goods_sku(
    message: Message,
    dialog: ManagedDialogAdapterProto,
    manager: DialogManager,
    **kwargs,
):
    manager.current_context().dialog_data[GOODS_SKU] = message.text
    await dialog.next()


async def add_goods_yes_no(
    query: CallbackQuery,
    select: ManagedWidgetAdapter[Select],
    manager: DialogManager,
    item_id: str,
    **kwargs,
):
    goods_service: GoodsService = manager.data.get("goods_service")
    data = manager.current_context().dialog_data

    if item_id == NO:
        data["result"] = "Goods adding cancelled"
        await manager.done()
        return

    goods = GoodsCreate(
        name=data[GOODS_NAME],
        type=GoodsType(data[GOODS_TYPE]),
        parent_id=data.get(SELECTED_GOODS),
        sku=data.get(GOODS_SKU),
    )

    goods = await goods_service.add_goods(goods)

    result = fmt.pre(
        fmt.quote(
            f"Goods created\n\n"
            f"id:           {goods.id}\n"
            f"parent id:    {goods.parent_id}\n\n"
            f"name:         {goods.name}\n"
            f"type:         {'📁' if goods.type is GoodsType.FOLDER else '📦'}\n"
            f"sku:          {goods.sku}\n"
        )
    )
    data["result"] = result

    await manager.dialog().next()


async def result_getter(dialog_manager: DialogManager, **kwargs):
    return {"result": dialog_manager.current_context().dialog_data.get("result")}


async def back_from_confirm(
    query: CallbackQuery,
    button: ManagedWidgetAdapter[Button],
    manager: DialogManager,
    **kwargs,
):
    if manager.current_context().dialog_data.get(GOODS_SKU):
        await manager.dialog().back()
    else:
        await query.answer()
        await manager.dialog().switch_to(AddGoods.type)


add_goods_dialog = Dialog(
    Window(
        goods_adding_process,
        Const("Input goods name:"),
        MessageInput(request_goods_name),
        Row(Cancel(Const("❌ Cancel")), Next(Const("➡ Next️"), when=GOODS_NAME)),
        getter=get_goods_data,
        state=states.goods_db.AddGoods.name,
        parse_mode="HTML",
    ),
    Window(
        goods_adding_process,
        Const("Select goods type:"),
        Select(
            Format("{item[0]}"),
            id="goods_type",
            item_id_getter=itemgetter(1),
            items=[
                ("📁 Folder", GoodsType.FOLDER.value),
                ("📦 Goods", GoodsType.GOODS.value),
            ],
            on_click=save_goods_type,
        ),
        Row(
            Back(Const("🔙 Back")),
            Cancel(Const("❌ Cancel")),
            Next(Const("➡ Next️"), when=GOODS_TYPE),
        ),
        getter=get_goods_data,
        state=states.goods_db.AddGoods.type,
        parse_mode="HTML",
    ),
    Window(
        goods_adding_process,
        Const("Input SKU:"),
        MessageInput(request_goods_sku),
        Row(
            Back(Const("🔙 Back")),
            Cancel(Const("❌ Cancel")),
            Next(Const("➡ Next️"), when=GOODS_SKU),
        ),
        getter=get_goods_data,
        state=states.goods_db.AddGoods.sku,
        parse_mode="HTML",
    ),
    Window(
        goods_adding_process,
        Const("Confirm ?"),
        Select(
            Format("{item[0]}"),
            id="add_yes_no",
            item_id_getter=itemgetter(1),
            items=YES_NO,
            on_click=add_goods_yes_no,
        ),
        Row(
            Back(Const("🔙 Back"), on_click=back_from_confirm), Cancel(Const("❌ Cancel"))
        ),
        getter=get_goods_data,
        state=states.goods_db.AddGoods.confirm,
        parse_mode="HTML",
        preview_add_transitions=[Next()],
    ),
    Window(
        Format("{result}"),
        Cancel(Const("❌ Close"), on_click=enable_send_mode),
        getter=[get_goods_data, result_getter],
        state=states.goods_db.AddGoods.result,
        parse_mode="HTML",
    ),
    on_start=copy_start_data_to_context,
)
