from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.text import Format, Multi

from app.tgbot.constants import GOODS_NAME, GOODS_SKU, GOODS_TYPE
from app.tgbot.handlers.dialogs.common import when_not

goods_adding_process = Multi(
    Format(f"Goods name: {{{GOODS_NAME}}}", when=GOODS_NAME),
    Format(f"Goods name: ...", when=when_not(GOODS_NAME)),
    Format(f"Goods type: {{{GOODS_TYPE}}}", when=GOODS_TYPE),
    Format(f"Goods type: ...", when=when_not(GOODS_TYPE)),
    Format(f"Goods SKU: {{{GOODS_SKU}}}\n", when=GOODS_SKU),
    Format(f"GOODS SKU: ...\n", when=when_not(GOODS_SKU)),
)


async def get_goods_data(dialog_manager: DialogManager, **kwargs):
    dialog_data = dialog_manager.current_context().dialog_data

    return {
        GOODS_NAME: dialog_data.get(GOODS_NAME),
        GOODS_TYPE: dialog_data.get(GOODS_TYPE),
        GOODS_SKU: dialog_data.get(GOODS_SKU),
    }
