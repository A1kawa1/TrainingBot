from aiogram.fsm.state import StatesGroup, State


class StateForm(StatesGroup):
    GET_TIME_ZONE = State()
    GET_AGE = State()
    GET_HEIGHT = State()
    GET_CUR_WEIGHT = State()
    GET_TARGET_WEIGHT = State()
    GET_CUR_DCI = State()
    GET_FOOD = State()
    GET_NEW_DAY_DCI = State()
    GET_NEW_WEIGHT = State()
    GET_NEW_WEEK_EATING = State()
