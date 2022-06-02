from aiogram.dispatcher.fsm.state import State, StatesGroup


class AdminMenu(StatesGroup):
    category = State()


class UserCategory(StatesGroup):
    action = State()


class GoodsCategory(StatesGroup):
    action = State()


class MarketCategory(StatesGroup):
    action = State()
