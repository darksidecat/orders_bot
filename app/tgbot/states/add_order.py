from aiogram.dispatcher.fsm.state import State, StatesGroup


class AddOrder(StatesGroup):
    select_goods = State()
    input_quantity = State()
    select_market = State()
    input_comment = State()
    confirm = State()
    result = State()
