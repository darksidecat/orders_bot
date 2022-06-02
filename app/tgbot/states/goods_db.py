from aiogram.dispatcher.fsm.state import State, StatesGroup


class AddGoods(StatesGroup):
    name = State()
    type = State()
    sku = State()
    confirm = State()
    result = State()


class EditGoods(StatesGroup):
    select_goods = State()
    select_action = State()
    result = State()


class EditGoodsName(StatesGroup):
    request = State()


class EditGoodsType(StatesGroup):
    request = State()


class EditGoodsSKU(StatesGroup):
    request = State()


class EditGoodsActiveStatus(StatesGroup):
    request = State()
