from aiogram_dialog import Dialog, StartMode, Window
from aiogram_dialog.widgets.kbd import Cancel, Start
from aiogram_dialog.widgets.text import Const

from app.tgbot.states.admin_menu import GoodsCategory
from app.tgbot.states.goods_db import AddGoods, DeleteGoods, EditGoods

goods_menu_dialog = Dialog(
    Window(
        Const("Goods\n\n Select action"),
        Start(Const("Add"), id="add_user", state=AddGoods.name, mode=StartMode.NORMAL),
        Start(
            Const("Edit"),
            id="edit_user",
            state=EditGoods.select_goods,
            mode=StartMode.NORMAL,
        ),
        Start(
            Const("Delete"),
            id="delete_user",
            state=DeleteGoods.select_goods,
            mode=StartMode.NORMAL,
        ),
        Cancel(),
        state=GoodsCategory.action,
    ),
)
