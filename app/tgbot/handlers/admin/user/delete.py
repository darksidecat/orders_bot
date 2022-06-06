from operator import attrgetter, itemgetter

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Back, Cancel, Next, Row, ScrollingGroup, Select
from aiogram_dialog.widgets.managed import ManagedWidgetAdapter
from aiogram_dialog.widgets.text import Const, Format

from app.domain.user.exceptions.user import CantDeleteWithOrders
from app.domain.user.usecases.user import UserService
from app.tgbot import states
from app.tgbot.constants import NO, USER_ID, USERS, YES_NO
from app.tgbot.handlers.admin.user.common import get_user, get_users, save_user_id
from app.tgbot.handlers.dialogs.common import enable_send_mode, get_result


async def delete_user_yes_no(
    query: CallbackQuery,
    select_: ManagedWidgetAdapter[Select],
    manager: DialogManager,
    item_id: str,
):
    user_service: UserService = manager.data.get("user_service")
    data = manager.current_context().dialog_data

    if item_id == NO:
        await query.answer("User deleting cancelled", show_alert=True)
        await manager.dialog().back()
        return
    try:
        await user_service.delete_user(int(data[USER_ID]))
    except CantDeleteWithOrders:
        await query.answer("User can't be deleted because he has orders", show_alert=True)
        await manager.dialog().back()
        return
    data["result"] = f"User {data[USER_ID]} deleted"
    await manager.dialog().next()

    await query.answer()


delete_user_dialog = Dialog(
    Window(
        Const("Select user for deleting:"),
        ScrollingGroup(
            Select(
                Format("{item.name} {item.id}"),
                id=USER_ID,
                item_id_getter=attrgetter("id"),
                items=USERS,
                on_click=save_user_id,
            ),
            id="user_scrolling",
            width=1,
            height=5,
        ),
        Cancel(),
        getter=get_users,
        state=states.user_db.DeleteUser.select_user,
        preview_add_transitions=[Next()],
    ),
    Window(
        Format("User:\n\n  id: {user.id}\n  name:   {user.name}\n\nDelete?"),
        Select(
            Format("{item[0]}"),
            id="delete_yes_no",
            item_id_getter=itemgetter(1),
            items=YES_NO,
            on_click=delete_user_yes_no,
        ),
        Row(Back(), Cancel()),
        getter=get_user,
        state=states.user_db.DeleteUser.confirm,
        preview_add_transitions=[Next()],
    ),
    Window(
        Format("{result}"),
        Cancel(Const("Close"), on_click=enable_send_mode),
        getter=get_result,
        state=states.user_db.DeleteUser.result,
        parse_mode="HTML",
    ),
)
