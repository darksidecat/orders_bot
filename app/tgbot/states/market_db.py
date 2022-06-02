from aiogram.dispatcher.fsm.state import State, StatesGroup


class AddMarket(StatesGroup):
    name = State()
    confirm = State()
    result = State()


class EditMarket(StatesGroup):
    select_goods = State()
    select_action = State()
    result = State()


class EditMarketName(StatesGroup):
    request = State()
