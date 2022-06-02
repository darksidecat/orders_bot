from aiogram_dialog import Dialog, StartMode, Window
from aiogram_dialog.widgets.kbd import Cancel, Start
from aiogram_dialog.widgets.text import Const

from app.tgbot.states.admin_menu import MarketCategory
from app.tgbot.states.market_db import EditMarket

market_menu_dialog = Dialog(
    Window(
        Const("Market\n\n Select action"),
        Start(
            Const("Add/Edit"),
            id="edit_market",
            state=EditMarket.select_market,
            mode=StartMode.NORMAL,
        ),
        Cancel(),
        state=MarketCategory.action,
    ),
)
