from aiogram.dispatcher.fsm.state import State, StatesGroup


class Help(StatesGroup):
    show = State()
