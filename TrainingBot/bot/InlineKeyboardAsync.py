from datetime import datetime
from bot.config import TYPE, ACTIVITY
from model.models import (User, UserStageGuide, TargetUser)

from aiogram.types import (ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardButton, InlineKeyboardMarkup)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.SqlQueryAsync import *


async def create_keyboard_stage(id):
    stage = await get_stage(id)
    if stage == -1:
        return ReplyKeyboardRemove()
    elif stage == 0:
        buttons = ('Мои данные', 'Сброс')
    elif stage == 1:
        buttons = ('Мои данные', 'Моя цель', 'Сброс')
    elif stage == 2:
        buttons = ('Мои данные', 'Моя цель', 'Сброс')
    elif stage == 3:
        buttons = ('Мои данные', 'Моя цель', 'Мастер обучения',
                   'Начать сбор данных', 'Я знаю сколько я ем сейчас', 'Сброс')
    elif stage == 4:
        buttons = ('Мастер обучения', 'Меню',
                   'Статистика за день', 'Мониторинг',
                   'Мои данные', 'Моя цель', 'Сброс')
    elif stage == 5:
        buttons = ('Мои данные', 'Моя программа', 'Меню',
                   'Мастер обучения', 'Статистика за день',
                   'Статистика за неделю', 'Сброс')

    buttons = [[KeyboardButton(text=button) for button in buttons]]

    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


async def last_message(mesKey):
    if mesKey == 'start_last':
        buttons = [[
            InlineKeyboardButton(
                text='Начать работу',
                callback_data='login'
            )
        ]]
    elif mesKey == 'stage1_last':
        buttons = [[
            InlineKeyboardButton(
                text='Создать цель',
                callback_data='create_target'
            )
        ]]
    elif mesKey == 'stage2_last':
        buttons = [[
            InlineKeyboardButton(
                text='Начать обучение',
                callback_data='start_guide'
            )],
            [InlineKeyboardButton(
                text='Перейти на следующий уровень',
                callback_data='skip_guide'
            )
        ]]
    elif mesKey == 'stage3_last':
        buttons = [[
            InlineKeyboardButton(
                text='Начать сбор данных',
                callback_data='start_get_cur_DCI'
            )],
            [InlineKeyboardButton(
                text='Я знаю сколько я ем сейчас',
                callback_data='get_cur_DCI'
            )
        ]]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def create_InlineKeyboard_user_info(id):
    info = await InfoUser.objects.aget(user=id)
    stage = await UserStageGuide.objects.aget(user=id)
    buttons = []

    field = {
        'Возраст': ['age', info.age, 'лет'],
        'Рост': ['height', info.height, 'см'],
        'Пол': ['gender', info.gender, ''],
        'Ваш идельный вес': ['asdvsdfg', info.ideal_weight, 'кг'],
        'Этап': ['asdvsdfg', stage.stage, ''],
    }
    for text in field.keys():
        if text == 'Ваш идельный вес':
            buttons.append([InlineKeyboardButton(
                text=f'{text} - {field[text][1]} {field[text][2]}',
                url='https://alfagym.ru/wp-content/uploads/b/2/9/b2950dc181b1a619dc1075995da6f7f1.jpg'
            )])
        else:
            buttons.append([InlineKeyboardButton(
                text=f'{text} - {field[text][1]} {field[text][2]}',
                callback_data=f'change_{field[text][0]}'
            )])

    buttons.append([InlineKeyboardButton(
        text='Закрыть',
        callback_data='close'
    )])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def create_InlineKeyboard_gender():
    buttons = []
    buttons.append([InlineKeyboardButton(
        text='М',
        callback_data='men'
    )])
    buttons.append([InlineKeyboardButton(
        text='Ж',
        callback_data='woomen'
    )])
    buttons.append([InlineKeyboardButton(
        text='Назад',
        callback_data='my_info'
    )])
    buttons.append([InlineKeyboardButton(
        text='Закрыть',
        callback_data='close'
    )])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def create_InlineKeyboard_target(message):
    buttons = []
    id = message.chat.id
    target = await TargetUser.objects.filter(user=id).alast()

    if (target.type is None) or (target.type == 'None'):
        for el in TYPE:
            buttons.append([InlineKeyboardButton(
                text=el,
                callback_data=el
            )])
        buttons.append([InlineKeyboardButton(
            text='Закрыть',
            callback_data='close'
        )])

    elif target.type == TYPE[1]:
        field = {
            'Цель': ['asdvsdfg', target.type, ''],
            'Текущий вес': ['change_weight', target.cur_weight, 'кг'],
            'Вес, который хотим': ['change_target', target.target_weight, 'кг'],
            'Активность': ['change_activity', target.activity, ''],
            'DCI': ['asdvsdfg', target.dci, 'кКЛ'],
        }

        for text in field.keys():
            if text == 'DCI':
                buttons.append([InlineKeyboardButton(
                    text=f'{text} - {field[text][1]} {field[text][2]}',
                    url='https://mosturnik.ru/wp-content/uploads/a/9/0/a90e1467657b49e550142394e234c4d6.jpeg'
                )])
            else:
                buttons.append([InlineKeyboardButton(
                    text=f'{text} - {field[text][1]} {field[text][2]}',
                    callback_data=f'{field[text][0]}'
                )])

        buttons.append([InlineKeyboardButton(
            text='Назад',
            callback_data='my_target'
        )])
        buttons.append([InlineKeyboardButton(
            text='Закрыть',
            callback_data='close'
        )])
    else:
        buttons.append([InlineKeyboardButton(
            text=target.type,
            callback_data='asdvsdfg'
        )])
        buttons.append([InlineKeyboardButton(
            text=f'пока не придумал',
            callback_data='hold_weight'
        )])
        buttons.append([InlineKeyboardButton(
            text='Назад',
            callback_data='my_target'
        )])
        buttons.append([InlineKeyboardButton(
            text='Закрыть',
            callback_data='close'
        )])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def create_InlineKeyboard_activity():
    buttons = []
    for el in list(ACTIVITY.keys())[:-1]:
        buttons.append([InlineKeyboardButton(
            text=el,
            callback_data=el
        )])
    buttons.append([InlineKeyboardButton(
        text='Назад',
        callback_data='my_cur_target'
    )])
    buttons.append([InlineKeyboardButton(
        text='Закрыть',
        callback_data='close'
    )])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def create_InlineKeyboard_guide():
    buttons_keyboard = [[KeyboardButton(text='Завершить обучение')]]
    buttons_markup = []

    buttons_markup.append([InlineKeyboardButton(
        text='Пройти курс',
        url=f'https://changeyourbody.ru/kak-schitat-kalorii'
    )])
    buttons_markup.append([InlineKeyboardButton(
        text='Завершить обучение',
        callback_data='skip_guide'
    )])

    return (InlineKeyboardMarkup(inline_keyboard=buttons_markup),
            ReplyKeyboardMarkup(keyboard=buttons_keyboard, resize_keyboard=True))
