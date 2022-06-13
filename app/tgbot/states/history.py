from aiogram.dispatcher.fsm.state import StatesGroup, State


class History(StatesGroup):
    select_history_level = State()
