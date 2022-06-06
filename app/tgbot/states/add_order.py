from aiogram.dispatcher.fsm.state import State, StatesGroup


class AddOrder(StatesGroup):
    select_goods = State()