from aiogram.types import (ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardButton, InlineKeyboardMarkup)
from aiogram.types.web_app_info import WebAppInfo
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot.config import TYPE, ACTIVITY
from bot.SqlQueryAsync import *
from model.models import *


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

    builder = ReplyKeyboardBuilder()

    for button in buttons:
        builder.add(KeyboardButton(text=button))
    builder.adjust(3)

    return builder.as_markup(resize_keyboard=True)


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
                callback_data='skip_guide_stage_2'
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
                web_app=WebAppInfo(
                    url='https://alfagym.ru/wp-content/uploads/b/2/9/b2950dc181b1a619dc1075995da6f7f1.jpg')
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
                    web_app=WebAppInfo(
                        url='https://mosturnik.ru/wp-content/uploads/a/9/0/a90e1467657b49e550142394e234c4d6.jpeg')
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


async def create_InlineKeyboard_guide(id):
    buttons_markup = []
    buttons_markup.append([InlineKeyboardButton(
        text='Пройти курс',
        web_app=WebAppInfo(
            url='https://changeyourbody.ru/kak-schitat-kalorii')
    )])

    if await get_stage(id) == 2:
        buttons_keyboard = [[KeyboardButton(text='Завершить обучение')]]

        buttons_markup.append([InlineKeyboardButton(
            text='Завершить обучение',
            callback_data='skip_guide'
        )])
    else:
        buttons_keyboard = [[KeyboardButton(text='Я все вспомнил')]]

        buttons_markup.append([InlineKeyboardButton(
            text='Я все вспомнил',
            callback_data='skip_guide'
        )])

    return (InlineKeyboardMarkup(inline_keyboard=buttons_markup),
            ReplyKeyboardMarkup(keyboard=buttons_keyboard, resize_keyboard=True))


async def create_InlineKeyboard_program(id):
    user = await User.objects.aget(id=id)
    target = await TargetUser.objects.filter(user=user).alast()
    program = await UserProgram.objects.filter(target=target).alast()
    buttons = []

    buttons.append([InlineKeyboardButton(
        text=(f'Цель: похудеть c {target.cur_weight} кг '
              f'до {target.target_weight} кг'),
        callback_data='adfsgd'
    )])
    buttons.append([InlineKeyboardButton(
        text=f'Дата начала: {program.date_start}',
        callback_data='adfsgd'
    )])
    # markup.add(
    #     telebot.types.InlineKeyboardButton(
    #         text=f'Рацион в начале: {program.start_dci} кКл',
    #         callback_data='adfsgd'
    #     )
    # )
    buttons.append([InlineKeyboardButton(
        text=f'Норма потребления: {target.dci} кКл',
        callback_data='adfsgd'
    )])
    buttons.append([InlineKeyboardButton(
        text=f'Фаза 1: {program.phase1} дней',
        callback_data='adfsgd'
    )])

    buttons.append([InlineKeyboardButton(
        text=f'Фаза 2: {program.phase2} дней',
        callback_data='adfsgd'
    )])
    buttons.append([InlineKeyboardButton(
        text=f'Прошло дней: {program.cur_day}',
        callback_data='adfsgd'
    )])
    buttons.append([InlineKeyboardButton(
        text=f'Текущий рацион: {program.cur_dci} кКл',
        callback_data='adfsgd'
    )])

    buttons.append([InlineKeyboardButton(
        text=f'Текущий вес: {program.cur_weight} кг',
        callback_data='adfsgd'
    )])
    buttons.append([InlineKeyboardButton(
        text=f'Достижение цели: {program.achievement}%',
        callback_data='adfsgd'
    )])
    buttons.append([InlineKeyboardButton(
        text='Изменить текущую цель',
        callback_data='change_cur_target'
    )])
    buttons.append([InlineKeyboardButton(
        text='Указать текущий вес',
        callback_data='change_weight_in_program'
    )])
    buttons.append([InlineKeyboardButton(
        text='Закрыть',
        callback_data='close'
    )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def create_InlineKeyboard_food(id):
    foods = UserFood.objects.filter(user=id)
    buttons = []

    if await foods.aexists():
        async for food in foods:
            if food.name is None:
                text = f'{food.calories}'
            else:
                text = f'{food.name} - {food.calories}'
            buttons.append([InlineKeyboardButton(
                text=text,
                callback_data=f'food_{food.name}_{food.calories}'
            )])

    buttons.append([InlineKeyboardButton(
        text='Добавить блюдо',
        callback_data='add_food'
    )])
    buttons.append([InlineKeyboardButton(
        text='Закрыть',
        callback_data='close'
    )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def create_InlineKeyboard_day_food(id, time):
    user = await User.objects.aget(id=id)
    buttons = []

    foods = user.day_food.filter(
        time__year=time.year,
        time__month=time.month,
        time__day=time.day
    ).order_by('-time')

    async for food in foods:
        id = food.id
        name = food.name
        calories = food.calories
        time = food.time

        if name is None:
            text = f'{time.hour:02}:{time.minute:02} - {calories}кКл'
        else:
            text = f'{time.hour:02}:{time.minute:02} - {name} {calories}кКл'

        buttons.append([InlineKeyboardButton(
            text=text,
            callback_data=f'detail_{id}'
        )])

    buttons.append([InlineKeyboardButton(
        text='Закрыть',
        callback_data='close'
    )])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def create_InlineKeyboard_detail_day_food(food_id):
    buttons = []

    buttons.append([InlineKeyboardButton(
        text='Изменить',
        callback_data=f'change_day_dci_{food_id}'
    )])
    buttons.append([InlineKeyboardButton(
        text='Удалить',
        callback_data=f'delete_day_dci_{food_id}'
    )])
    buttons.append([InlineKeyboardButton(
        text='Назад',
        callback_data='back_day_food'
    )])
    buttons.append([InlineKeyboardButton(
        text='Закрыть',
        callback_data='close'
    )])

    return InlineKeyboardMarkup(inline_keyboard=buttons)
