from uuid import UUID

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const

from app.domain.market.dto import Market
from app.domain.order.dto import OrderCreate, OrderLine
from app.domain.order.usecases.order import OrderService
from app.tgbot.states import add_order


async def add_new_order(
    event: CallbackQuery, button, dialog_manager: DialogManager, ** kwargs

):
    order_service: OrderService = dialog_manager.data.get("order_service")
    order_lines = [OrderLine(goods_id=UUID("83588027-7f53-40d9-b7ff-934476923f59"), quantity=100), OrderLine(goods_id=UUID("83588027-7f53-40d9-b7ff-934476923f59"), quantity=100)]
    order_data = OrderCreate(
        order_lines=order_lines,
        creator_id=event.from_user.id,
        recipient_market_id=UUID("43c500e3-2d9a-4f2b-9dbc-1e33ab7077f5"),
        commentary="test"
    )

    await order_service.add_order(order_data)


add_order_dialog = Dialog(
    Window(
        Const("Select goods"),
        Button(Const("add_good"), id="1", on_click=add_new_order),
        state=add_order.AddOrder.select_goods,
    )
)