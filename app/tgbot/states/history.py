from aiogram.dispatcher.fsm.state import State, StatesGroup


class History(StatesGroup):
    select_history_level = State()
    show = State()
