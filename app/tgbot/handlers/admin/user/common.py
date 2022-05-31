from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Multiselect, Select
from aiogram_dialog.widgets.managed import ManagedWidgetAdapter
from aiogram_dialog.widgets.text import Format, Multi

from app.domain.access_levels.interfaces.uow import IAccessLevelUoW
from app.domain.access_levels.usecases.access_levels import (
    AccessLevelsService,
    GetAccessLevels,
)
from app.domain.user.exceptions.user import UserNotExists
from app.domain.user.interfaces.uow import IUserUoW
from app.domain.user.usecases.user import GetUser, GetUsers, UserService
from app.tgbot.constants import ACCESS_LEVELS, USER, USER_ID, USER_NAME, USERS
from app.tgbot.handlers.dialogs.common import when_not


async def get_users(dialog_manager: DialogManager, user_service: UserService, **kwargs):
    users = await user_service.get_users()
    return {USERS: users}


async def save_user_id(
    query: CallbackQuery,
    select: ManagedWidgetAdapter[Select],
    manager: DialogManager,
    item_id: str,
):
    manager.current_context().dialog_data[USER_ID] = item_id
    await manager.dialog().next()
    await query.answer()


async def get_user(dialog_manager: DialogManager, user_service: UserService, **kwargs):
    user_id = dialog_manager.current_context().dialog_data[USER_ID]
    try:
        user = await user_service.get_user(int(user_id))
    except UserNotExists:  # ToDo check if need
        user = None
    return {USER: user}


user_adding_process = Multi(
    Format(f"<pre>User id:       {{{USER_ID}}}</pre>", when=USER_ID),
    Format(f"<pre>User id:       ...</pre>", when=when_not(USER_ID)),
    Format(f"<pre>User name:     {{{USER_NAME}}}</pre>", when=USER_NAME),
    Format(f"<pre>User name:     ...</pre>", when=when_not(USER_NAME)),
    Format(f"<pre>Access levels: {{{ACCESS_LEVELS}}}</pre>\n", when=ACCESS_LEVELS),
    Format(f"<pre>Access levels: ...</pre>\n", when=when_not(ACCESS_LEVELS)),
)


async def get_user_data(
    dialog_manager: DialogManager, access_levels_service: AccessLevelsService, **kwargs
):
    dialog_data = dialog_manager.current_context().dialog_data

    levels = []
    levels_ids = dialog_data.get(ACCESS_LEVELS)
    if levels_ids:
        all_levels = await access_levels_service.get_access_levels()
        for level in all_levels:
            if str(level.id) in levels_ids:
                levels.append(level)

    return {
        USER_ID: dialog_data.get(USER_ID),
        USER_NAME: dialog_data.get(USER_NAME),
        ACCESS_LEVELS: ", ".join((level.name.name for level in levels)),
    }


async def save_selected_access_levels(
    event: CallbackQuery, button, manager: DialogManager, **kwargs
):

    access_levels: Multiselect = manager.dialog().find(ACCESS_LEVELS)
    selected_levels = access_levels.get_checked(manager)

    if not selected_levels:
        await event.answer("select at least one level")
        return

    manager.current_context().dialog_data[ACCESS_LEVELS] = selected_levels
    await manager.dialog().next()


async def copy_start_data_to_context(_, dialog_manager: DialogManager):
    dialog_manager.current_context().dialog_data.update(
        dialog_manager.current_context().start_data
    )
