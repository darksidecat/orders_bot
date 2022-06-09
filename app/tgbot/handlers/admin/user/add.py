from operator import itemgetter

from aiogram.types import CallbackQuery, Message
from aiogram.utils.text_decorations import html_decoration as fmt
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.manager.protocols import ManagedDialogAdapterProto
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import (
    Back,
    Button,
    Cancel,
    Column,
    Multiselect,
    Next,
    Row,
    Select,
)
from aiogram_dialog.widgets.managed import ManagedWidgetAdapter
from aiogram_dialog.widgets.text import Const, Format

from app.domain.access_levels.usecases.access_levels import AccessLevelsService
from app.domain.user.dto.user import UserCreate
from app.domain.user.exceptions.user import BlockedUserWithOtherRole, UserAlreadyExists
from app.domain.user.usecases.user import UserService
from app.tgbot import states
from app.tgbot.constants import ALL_ACCESS_LEVELS, NO, USER_ID, YES_NO
from app.tgbot.handlers.admin.user.common import (
    ACCESS_LEVELS,
    USER_NAME,
    get_user_data,
    save_selected_access_levels,
    user_adding_process,
)
from app.tgbot.handlers.dialogs.common import enable_send_mode, get_result


async def request_id(
    message: Message, dialog: ManagedDialogAdapterProto, manager: DialogManager
):
    if not message.text.isdigit():
        await message.answer("User id must be a number")
        return

    manager.current_context().dialog_data[USER_ID] = message.text
    await dialog.next()


async def request_name(
    message: Message, dialog: ManagedDialogAdapterProto, manager: DialogManager
):
    manager.current_context().dialog_data[USER_NAME] = message.text
    await dialog.next()


async def get_access_levels(
    dialog_manager: DialogManager, access_levels_service: AccessLevelsService, **kwargs
):
    access_levels = await access_levels_service.get_access_levels()
    access_levels = [(level.name.name, level.id) for level in access_levels]

    access_levels = {
        ALL_ACCESS_LEVELS: access_levels,
    }
    user_data = await get_user_data(dialog_manager, access_levels_service)

    return user_data | access_levels


async def add_user_yes_no(
    query: CallbackQuery,
    select: ManagedWidgetAdapter[Select],
    manager: DialogManager,
    item_id: str,
):
    user_service: UserService = manager.data.get("user_service")
    data = manager.current_context().dialog_data

    if item_id == NO:
        await query.answer("User adding cancelled")
        await manager.done()
        return

    user = UserCreate(
        id=data[USER_ID], name=data[USER_NAME], access_levels=data[ACCESS_LEVELS]
    )
    try:
        new_user = await user_service.add_user(user)
        levels_names = ", ".join((level.name.name for level in new_user.access_levels))

        result = fmt.pre(
            f"User created\n"
            f"id:           {data[USER_ID]}\n"
            f"name:         {fmt.quote(data[USER_NAME])}\n"
            f"access level: {levels_names}\n"
        )
        data["result"] = result

    except UserAlreadyExists:
        data["result"] = "User already exist"

    except BlockedUserWithOtherRole:
        await query.answer("Blocked user can have only that role")
        return

    await manager.dialog().next()
    await query.answer()


add_user_dialog = Dialog(
    Window(
        user_adding_process,
        Const("Input user id:"),
        MessageInput(request_id),
        Row(Cancel(Const("❌ Cancel")), Next(Const("➡ Next️"), when=USER_ID)),
        getter=get_user_data,
        state=states.user_db.AddUser.id,
        parse_mode="HTML",
    ),
    Window(
        user_adding_process,
        Format("Input user name:"),
        MessageInput(request_name),
        Row(
            Back(Const("⬅️ Back")),
            Cancel(Const("❌ Cancel")),
            Next(Const("➡ Next️"), when=USER_NAME),
        ),
        getter=get_user_data,
        state=states.user_db.AddUser.name,
        parse_mode="HTML",
    ),
    Window(
        user_adding_process,
        Const("Select access level"),
        Column(
            Multiselect(
                Format("✓ {item[0]}"),
                Format("{item[0]}"),
                id=ACCESS_LEVELS,
                item_id_getter=itemgetter(1),
                items=ALL_ACCESS_LEVELS,
            )
        ),
        Button(
            Const("💾 Save"),
            id="save_access_levels",
            on_click=save_selected_access_levels,
        ),
        Row(
            Back(Const("⬅️ Back")),
            Cancel(Const("❌ Cancel")),
            Next(Const("➡ Next️"), when=ACCESS_LEVELS),
        ),
        getter=get_access_levels,
        state=states.user_db.AddUser.access_level,
        parse_mode="HTML",
    ),
    Window(
        user_adding_process,
        Const("Confirm ?"),
        Select(
            Format("{item[0]}"),
            id="add_yes_no",
            item_id_getter=itemgetter(1),
            items=YES_NO,
            on_click=add_user_yes_no,
        ),
        Row(Back(Const("⬅️ Back")), Cancel(Const("❌ Cancel"))),
        getter=get_user_data,
        state=states.user_db.AddUser.confirm,
        parse_mode="HTML",
        preview_add_transitions=[Next()],
    ),
    Window(
        Format("{result}"),
        Cancel(Const("❌ Close"), on_click=enable_send_mode),
        getter=get_result,
        state=states.user_db.AddUser.result,
        parse_mode="HTML",
    ),
)
