from aiogram.dispatcher.fsm.state import State, StatesGroup


class MainMenu(StatesGroup):
    select_option = State()
