from aiogram.dispatcher.fsm.state import State, StatesGroup


class AddUser(StatesGroup):
    id = State()
    name = State()
    access_level = State()
    confirm = State()
    result = State()


class DeleteUser(StatesGroup):
    select_user = State()
    confirm = State()
    result = State()


class EditUser(StatesGroup):
    select_user = State()
    select_field = State()
    result = State()


class EditUserId(StatesGroup):
    request = State()


class EditUserName(StatesGroup):
    request = State()


class EditAccessLevel(StatesGroup):
    request = State()
