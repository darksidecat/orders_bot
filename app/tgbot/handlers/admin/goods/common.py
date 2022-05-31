from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.text import Format, Multi

from app.tgbot.constants import GOODS_NAME, GOODS_SKU, GOODS_TYPE
from app.tgbot.handlers.dialogs.common import when_not

goods_adding_process = Multi(
    Format(f"<pre>Goods name:       {{{GOODS_NAME}}}</pre>", when=GOODS_NAME),
    Format(f"<pre>Goods name:       ...</pre>", when=when_not(GOODS_NAME)),
    Format(f"<pre>Goods type:       {{{GOODS_TYPE}}}</pre>", when=GOODS_TYPE),
    Format(f"<pre>Goods type:       ...</pre>", when=when_not(GOODS_TYPE)),
    Format(f"<pre>Goods SKU:        {{{GOODS_SKU}}}</pre>\n", when=GOODS_SKU),
    Format(f"<pre>GOODS SKU:        ...</pre>\n", when=when_not(GOODS_SKU)),
)


async def get_goods_data(dialog_manager: DialogManager, **kwargs):
    dialog_data = dialog_manager.current_context().dialog_data

    return {
        GOODS_NAME: dialog_data.get(GOODS_NAME),
        GOODS_TYPE: dialog_data.get(GOODS_TYPE),
        GOODS_SKU: dialog_data.get(GOODS_SKU),
    }
