import uuid
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
    Row,
    ScrollingGroup,
    Select,
    Start,
)
from aiogram_dialog.widgets.managed import ManagedWidgetAdapter
from aiogram_dialog.widgets.text import Const, Format

from app.domain.goods.dto import Goods, GoodsPatch
from app.domain.goods.exceptions.goods import (
    CantDeleteWithChildren,
    CantMakeInactiveWithActiveChildren,
    GoodsNotExists,
)
from app.domain.goods.models.goods_type import GoodsType
from app.domain.goods.usecases.goods import GoodsService
from app.tgbot import states
from app.tgbot.constants import GOODS, OLD_GOODS_ID, SELECTED_GOODS
from app.tgbot.handlers.admin.user.common import copy_start_data_to_context

ROOT_GOODS = Goods(
    parent_id=None, name="Root", type=GoodsType.FOLDER, is_active=True, id=uuid.uuid4()
)


async def go_to_next_level(
    query: CallbackQuery,
    select: ManagedWidgetAdapter[Select],
    manager: DialogManager,
    item_id: str,
):
    goods_service: GoodsService = manager.data.get("goods_service")

    manager.current_context().dialog_data[OLD_GOODS_ID] = item_id
    manager.current_context().dialog_data[SELECTED_GOODS] = item_id
    if (await goods_service.get_goods_by_id(UUID(item_id))).type == GoodsType.GOODS:
        await manager.dialog().next()
    await manager.dialog().show()


async def get_goods(
    dialog_manager: DialogManager, goods_service: GoodsService, **kwargs
):
    parent_id = dialog_manager.current_context().dialog_data.get(SELECTED_GOODS)
    parent_id_as_uuid = UUID(str(parent_id)) if parent_id else None
    goods = await goods_service.get_goods_in_folder(parent_id_as_uuid)
    return {GOODS: goods}


async def get_current_goods(
    dialog_manager: DialogManager, goods_service: GoodsService, **kwargs
):
    goods_id = dialog_manager.current_context().dialog_data.get(SELECTED_GOODS)
    if not goods_id:
        current_goods = None
    else:
        goods_id_as_uuid = UUID(str(goods_id)) if goods_id else None
        current_goods = await goods_service.get_goods_by_id(goods_id_as_uuid)
    data = (
        f"""
Selected now
ID: {current_goods.id}
Name: {current_goods.name}
SKU: {current_goods.sku}
Type: {current_goods.type}
Active: {current_goods.is_active}
Parent ID: {current_goods.parent_id}
"""
        if current_goods
        else ""
    )
    return {"current_goods_data": data}


async def selected_goods_data(dialog_manager: DialogManager, **kwargs):
    return {
        SELECTED_GOODS: dialog_manager.current_context().dialog_data.get(SELECTED_GOODS)
    }


async def add_new_goods(
    query: CallbackQuery, button: Button, manager: DialogManager, **kwargs
):
    data_for_copy = {
        SELECTED_GOODS: manager.current_context().dialog_data.get(SELECTED_GOODS)
    }
    await manager.start(states.goods_db.AddGoods.name, data=data_for_copy)


async def edit_this_folder(
    query: CallbackQuery, button: Button, manager: DialogManager, **kwargs
):
    await manager.switch_to(states.goods_db.EditGoods.select_field)


async def change_active_status(
    query: CallbackQuery, button: Button, manager: DialogManager, **kwargs
):
    goods_service: GoodsService = manager.data.get("goods_service")

    parent_id = manager.current_context().dialog_data.get(SELECTED_GOODS)
    parent_id_as_uuid = UUID(parent_id) if parent_id is not None else None
    try:
        await goods_service.change_goods_status(parent_id_as_uuid)
    except CantMakeInactiveWithActiveChildren:
        await query.answer("Can't make inactive with active children")
    await manager.dialog().back()


async def delete_goods(
    query: CallbackQuery, button: Button, manager: DialogManager, **kwargs
):
    goods_service: GoodsService = manager.data.get("goods_service")

    parent_id = manager.current_context().dialog_data.get(SELECTED_GOODS)
    try:
        await goods_service.delete_goods(UUID(parent_id))
    except CantDeleteWithChildren:
        await query.answer("Can't delete with children")
        return

    await query.answer("Goods deleted")
    manager.current_context().dialog_data[SELECTED_GOODS] = None
    await manager.dialog().switch_to(states.goods_db.EditGoods.select_goods)


async def go_to_parent_folder(
    query: CallbackQuery, button: Button, manager: DialogManager, **kwargs
):
    goods_service: GoodsService = manager.data.get("goods_service")
    parent_id = manager.current_context().dialog_data.get(SELECTED_GOODS)
    parent_id_as_uuid = UUID(parent_id) if parent_id is not None else None
    try:
        goods = await goods_service.get_goods_by_id(parent_id_as_uuid)
    except GoodsNotExists:
        goods = ROOT_GOODS
    manager.current_context().dialog_data[SELECTED_GOODS] = (
        str(goods.parent_id) if goods.parent_id else None
    )
    await manager.dialog().show()
    await manager.dialog().switch_to(states.goods_db.EditGoods.select_goods)


async def edit_field_dialog_start(
    query: CallbackQuery, button: Button, manager: DialogManager, **kwargs
):
    data_for_copy = {
        SELECTED_GOODS: manager.current_context().dialog_data.get(SELECTED_GOODS)
    }
    if button.widget_id == "edit_name":
        await manager.start(states.goods_db.EditGoodsName.request, data=data_for_copy)
    elif button.widget_id == "edit_sku":
        await manager.start(states.goods_db.EditGoodsSKU.request, data=data_for_copy)
    else:
        raise ValueError(f"Unknown widget id: {button.widget_id}")


async def request_name(
    message: Message, dialog: ManagedDialogAdapterProto, manager: DialogManager
):
    service: GoodsService = manager.data.get("goods_service")
    selected_goods = UUID(manager.current_context().dialog_data.get(SELECTED_GOODS))
    await service.patch_goods(GoodsPatch(id=selected_goods, name=message.text))
    await manager.done()


async def request_sku(
    message: Message, dialog: ManagedDialogAdapterProto, manager: DialogManager
):
    service: GoodsService = manager.data.get("goods_service")
    selected_goods = UUID(manager.current_context().dialog_data.get(SELECTED_GOODS))
    await service.patch_goods(GoodsPatch(id=selected_goods, sku=message.text))
    await manager.done()


goods_name_dialog = Dialog(
    Window(
        Format("Input new name"),
        MessageInput(request_name),
        state=states.goods_db.EditGoodsName.request,
    ),
    on_start=copy_start_data_to_context,
)

goods_sku_dialog = Dialog(
    Window(
        Format("Input new SKU"),
        MessageInput(request_sku),
        state=states.goods_db.EditGoodsSKU.request,
    ),
    on_start=copy_start_data_to_context,
)


edit_goods_dialog = Dialog(
    Window(
        Const("Select goods for editing:"),
        Format("{current_goods_data}"),
        ScrollingGroup(
            Select(
                Format("{item.icon} {item.name} {item.sku_text} {item.active_icon}"),
                id=OLD_GOODS_ID,
                item_id_getter=attrgetter("id"),
                items=GOODS,
                on_click=go_to_next_level,
            ),
            id="goods_scrolling",
            width=1,
            height=8,
        ),
        Button(
            Const("Edit this Folder"),
            id="edit_folder",
            on_click=edit_this_folder,
            when=SELECTED_GOODS,
        ),
        Row(
            Button(Const("Add new"), on_click=add_new_goods, id="add_new_goods"),
            Button(
                Const("Back"), id="go_to_parent_folder", on_click=go_to_parent_folder
            ),
        ),
        Cancel(),
        getter=[get_goods, get_current_goods, selected_goods_data],
        state=states.goods_db.EditGoods.select_goods,
    ),
    Window(
        Format("{current_goods_data}"),
        Const("Select option"),
        Row(
            Button(
                Const("Edit name"), on_click=edit_field_dialog_start, id="edit_name"
            ),
            Button(Const("Edit sku"), on_click=edit_field_dialog_start, id="edit_sku"),
        ),
        Row(
            Button(
                Const("Invert active status"),
                on_click=change_active_status,
                id="mark_inactive",
            ),
            Button(Const("Delete"), on_click=delete_goods, id="delete_goods"),
        ),
        Row(
            Back(),
            Cancel(),
        ),
        getter=get_current_goods,
        state=states.goods_db.EditGoods.select_field,
    ),
)
