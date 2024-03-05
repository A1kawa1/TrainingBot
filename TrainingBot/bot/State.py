from aiogram.fsm.state import StatesGroup, State


class StateForm(StatesGroup):
    GET_AGE = State()
    GET_HEIGHT = State()
    GET_CUR_WEIGHT = State()
    GET_TARGET_WEIGHT = State()
    GET_CUR_DCI = State()
    GET_FOOD = State()
