from operator import attrgetter, itemgetter
from typing import Any, Union

from aiogram.types import CallbackQuery, Message
from aiogram.utils.text_decorations import html_decoration as fmt
from aiogram_dialog import Data, Dialog, DialogManager, Window
from aiogram_dialog.manager.protocols import ManagedDialogAdapterProto
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import (
    Button,
    Cancel,
    Column,
    Multiselect,
    Next,
    ScrollingGroup,
    Select,
    SwitchTo,
)
from aiogram_dialog.widgets.managed import ManagedWidgetAdapter
from aiogram_dialog.widgets.text import Const, Format, Multi

from app.domain.access_levels.interfaces.uow import IAccessLevelUoW
from app.domain.access_levels.usecases.access_levels import AccessLevelsService
from app.domain.user.dto.user import PatchUserData, UserPatch
from app.domain.user.exceptions.user import UserNotExists, BlockedUserWithOtherRole
from app.domain.user.interfaces.uow import IUserUoW
from app.domain.user.usecases.user import UserService
from app.infrastructure.database.models import TelegramUser
from app.tgbot import states
from app.tgbot.constants import (
    ACCESS_LEVELS,
    ALL_ACCESS_LEVELS,
    FIELD,
    OLD_USER_ID,
    USER,
    USER_ID,
    USER_NAME,
)
from app.tgbot.handlers.admin.user.common import (
    copy_start_data_to_context,
    get_user_data,
    get_users,
    user_adding_process,
)
from app.tgbot.handlers.dialogs.common import enable_send_mode, get_result

IUserAccessLevelUoW = Union[IUserUoW, IAccessLevelUoW]


async def save_user_id(
    query: CallbackQuery,
    select: ManagedWidgetAdapter[Select],
    manager: DialogManager,
    item_id: str,
):
    manager.current_context().dialog_data[OLD_USER_ID] = item_id
    await manager.dialog().next()
    await query.answer()


async def get_old_user(
    dialog_manager: DialogManager, user_service: UserService, **kwargs
):
    user_id = dialog_manager.current_context().dialog_data[OLD_USER_ID]
    try:
        user = await user_service.get_user(int(user_id))
    except UserNotExists:  # ToDo check if need
        user = None
    return {USER: user}


async def request_id(
    message: Message, dialog: ManagedDialogAdapterProto, manager: DialogManager
):
    if not message.text.isdigit():
        await message.answer("User id value must be digit")
        return

    await manager.done({USER_ID: message.text})


async def request_name(
    message: Message, dialog: ManagedDialogAdapterProto, manager: DialogManager
):
    await manager.done({USER_NAME: message.text})


async def on_field_selected(
    query: CallbackQuery,
    select: ManagedWidgetAdapter[Select],
    manager: DialogManager,
    item_id: str,
):
    column_states = {
        TelegramUser.id.name: states.user_db.EditUserId.request,
        TelegramUser.name.name: states.user_db.EditUserName.request,
        TelegramUser.access_levels.key: states.user_db.EditAccessLevel.request,
    }

    await manager.start(
        state=column_states[item_id],
        data=manager.current_context().dialog_data.copy(),
    )
    await query.answer()


async def get_user_edit_data(
    dialog_manager: DialogManager,
    user_service: UserService,
    access_levels_service: AccessLevelsService,
    **kwargs,
):
    user_id = dialog_manager.current_context().dialog_data[OLD_USER_ID]

    user = await user_service.get_user(int(user_id))
    fields = TelegramUser.__table__.columns.keys()
    fields.append(TelegramUser.access_levels.key)
    fields = [(f, f) for f in fields]

    dialog_manager.current_context().dialog_data[USER] = user.json()

    user_data = await get_user_data(dialog_manager, access_levels_service)

    return {USER: user, "fields": fields} | user_data


async def process_result(start_data: Data, result: Any, dialog_manager: DialogManager):
    if not result:
        return
    if result.get(USER_ID):
        dialog_manager.current_context().dialog_data[USER_ID] = result[USER_ID]
    if result.get(USER_NAME):
        dialog_manager.current_context().dialog_data[USER_NAME] = result[USER_NAME]
    if result.get(ACCESS_LEVELS):
        dialog_manager.current_context().dialog_data[ACCESS_LEVELS] = result[
            ACCESS_LEVELS
        ]


async def get_access_levels(
    dialog_manager: DialogManager,
    access_levels_service: AccessLevelsService,
    user_service: UserService,
    **kwargs,
):

    user_id = dialog_manager.current_context().dialog_data[OLD_USER_ID]
    access_levels = await access_levels_service.get_access_levels()

    init_check = dialog_manager.current_context().dialog_data.get("init_check")
    if init_check is None:
        user_access_levels = await access_levels_service.get_user_access_levels(
            int(user_id)
        )
        checked = dialog_manager.current_context().widget_data.setdefault(
            ACCESS_LEVELS, []
        )
        checked.extend(map(str, (level.id for level in user_access_levels)))
        dialog_manager.current_context().dialog_data["init_check"] = True

    access_levels = {
        ALL_ACCESS_LEVELS: [(level.name.name, level.id) for level in access_levels],
    }
    user_data = await get_old_user(dialog_manager, user_service)

    return user_data | access_levels


async def save_access_levels(
    query: CallbackQuery, button, dialog_manager: DialogManager, **kwargs
):
    access_levels: Multiselect = dialog_manager.dialog().find(ACCESS_LEVELS)
    selected_levels = access_levels.get_checked(dialog_manager)

    if not selected_levels:
        await query.answer("select at least one level")
        return

    if len(selected_levels) > 1 and '-1' in selected_levels:
        await query.answer("Blocked user can't have other roles")
        return

    await dialog_manager.done({ACCESS_LEVELS: selected_levels})


async def save_edited_user(
    query: CallbackQuery, button, dialog_manager: DialogManager, **kwargs
):
    user_service: UserService = dialog_manager.data.get("user_service")
    data = dialog_manager.current_context().dialog_data

    user = UserPatch(
        id=data[OLD_USER_ID],
        user_data=PatchUserData(
            id=data.get(USER_ID),
            name=data.get(USER_NAME),
            access_levels=data.get(ACCESS_LEVELS),
        ),
    )

    try:
        new_user = await user_service.patch_user(user)
    except BlockedUserWithOtherRole as err:
        await query.answer(str(err))
        return
    levels_names = ", ".join((level.name.name for level in new_user.access_levels))

    result = fmt.pre(
        fmt.quote(
            f"User {data[OLD_USER_ID]} edited\n\n"
            f"id:           {new_user.id}\n"
            f"name:         {new_user.name}\n"
            f"access level: {levels_names}\n"
        )
    )
    data["result"] = result

    await dialog_manager.dialog().next()
    await query.answer()


user_id_dialog = Dialog(
    Window(
        Format("Input new id for {user.id}"),
        MessageInput(request_id),
        Cancel(Const("❌ Cancel")),
        getter=get_old_user,
        state=states.user_db.EditUserId.request,
    ),
    on_start=copy_start_data_to_context,
)

user_name_dialog = Dialog(
    Window(
        Format("Input new name for {user.id}"),
        MessageInput(request_name),
        Cancel(Const("❌ Cancel")),
        getter=get_old_user,
        state=states.user_db.EditUserName.request,
    ),
    on_start=copy_start_data_to_context,
)

user_access_levels_dialog = Dialog(
    Window(
        Format("Select access levels for {user.id}"),
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
            on_click=save_access_levels,
        ),
        Cancel(Const("❌ Cancel")),
        getter=get_access_levels,
        state=states.user_db.EditAccessLevel.request,
    ),
    on_start=copy_start_data_to_context,
)


edit_user_dialog = Dialog(
    Window(
        Const("Select user for editing:"),
        ScrollingGroup(
            Select(
                Format("{item.name} {item.id}"),
                id=OLD_USER_ID,
                item_id_getter=attrgetter("id"),
                items="users",
                on_click=save_user_id,
            ),
            id="user_scrolling",
            width=1,
            height=8,
        ),
        Cancel(Const("❌ Cancel")),
        getter=get_users,
        state=states.user_db.EditUser.select_user,
        preview_add_transitions=[Next()],
    ),
    Window(
        Multi(
            Format("Selected user: {user.id}\nName: {user.name}\n\n"),
            user_adding_process,
        ),
        Column(
            Select(
                Format("{item[0]}"),
                id=FIELD,
                item_id_getter=itemgetter(1),
                items="fields",
                on_click=on_field_selected,
            ),
            Button(Const("Save"), id="save", on_click=save_edited_user),
            Cancel(Const("❌ Cancel")),
        ),
        getter=get_user_edit_data,
        state=states.user_db.EditUser.select_field,
        parse_mode="HTML",
        preview_add_transitions=[
            SwitchTo(Const(""), id="", state=states.user_db.EditUserId.request),
            SwitchTo(Const(""), id="", state=states.user_db.EditUserName.request),
            SwitchTo(Const(""), id="", state=states.user_db.EditAccessLevel.request),
            Next(),
        ],
    ),
    Window(
        Format("{result}"),
        Cancel(Const("❌ Close"), on_click=enable_send_mode),
        getter=get_result,
        state=states.user_db.EditUser.result,
        parse_mode="HTML",
    ),
    on_process_result=process_result,
)
