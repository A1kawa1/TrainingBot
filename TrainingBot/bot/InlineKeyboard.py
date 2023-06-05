import telebot
from datetime import datetime
import bot.SqlMain as SqlMain
from bot.config import TYPE
from model.models import (User, UserStageGuide, TargetUser)


def create_InlineKeyboard(user):
    markup = telebot.types.InlineKeyboardMarkup()
    if user[1] is None:
        markup.add(telebot.types.InlineKeyboardButton(
            text='Имя', callback_data='first_name'))
    else:
        markup.add(telebot.types.InlineKeyboardButton(
            text=user[1], callback_data='first_name'))
    if user[2] is None:
        markup.add(telebot.types.InlineKeyboardButton(
            text='Фамилия', callback_data='last_name'))
    else:
        markup.add(telebot.types.InlineKeyboardButton(
            text=user[2], callback_data='first_name'))
    if user[3] is None:
        markup.add(telebot.types.InlineKeyboardButton(
            text='Никнейм', callback_data='username'))
    else:
        markup.add(telebot.types.InlineKeyboardButton(
            text=user[3], callback_data='first_name'))
    if not user[3] is None:
        markup.add(telebot.types.InlineKeyboardButton(
            text='Войти', callback_data='login'))
    return markup


def create_InlineKeyboard_food(id):
    markup = telebot.types.InlineKeyboardMarkup()
    user = User.objects.get(id=id)
    foods = user.food.all()

    if foods.exists():
        for food in foods:
            if food.food.name is None:
                text = f'{food.food.calories}'
            else:
                text = f'{food.food.name} - {food.food.calories}'
            markup.add(telebot.types.InlineKeyboardButton(
                text=text,
                callback_data=f'food_{food.food.name}_{food.food.calories}'
            ))
    markup.add(telebot.types.InlineKeyboardButton(
        text='Добавить блюдо',
        callback_data='add_food'
    ))
    # markup.add(telebot.types.InlineKeyboardButton(
    #     text='Выбрать свое кол-во кКл',
    #     callback_data='own_food'
    # ))
    markup.add(telebot.types.InlineKeyboardButton(
        text='Закрыть',
        callback_data='close'
    ))
    return markup


def create_InlineKeyboard_user_info(message):
    info = SqlMain.get_info(message)
    if message.from_user.is_bot:
        id = message.chat.id
    else:
        id = message.from_user.id

    stage = UserStageGuide.objects.get(user=id)
    markup = telebot.types.InlineKeyboardMarkup()
    field = {
        'Возраст': ['age', info.age, 'лет'],
        'Рост': ['height', info.height, 'см'],
        'Пол': ['gender', info.gender, ''],
        'Ваш идельный вес': ['asdvsdfg', info.ideal_weight, 'кг'],
        'Этап': ['asdvsdfg', stage.stage, ''],
    }
    for text in field.keys():
        if text == 'Ваш идельный вес':
            markup.add(telebot.types.InlineKeyboardButton(
                text=f'{text} - {field[text][1]} {field[text][2]}',
                url='https://alfagym.ru/wp-content/uploads/b/2/9/b2950dc181b1a619dc1075995da6f7f1.jpg'
            ))
        else:
            markup.add(telebot.types.InlineKeyboardButton(
                text=f'{text} - {field[text][1]} {field[text][2]}',
                callback_data=f'change_{field[text][0]}'
            ))

    markup.add(telebot.types.InlineKeyboardButton(
        text='Закрыть',
        callback_data='close'
    ))
    return markup


def create_InlineKeyboard_target(message, flag=False):
    markup = telebot.types.InlineKeyboardMarkup()
    target = SqlMain.get_target(message)
    if (target.type is None) or (target.type == 'None') or flag:
        for el in TYPE:
            markup.add(telebot.types.InlineKeyboardButton(
                text=el,
                callback_data=el
            ))
        markup.add(telebot.types.InlineKeyboardButton(
            text='Закрыть',
            callback_data='close'
        ))

    elif target.type in TYPE[1:]:
        field = {
            'Цель': ['my_target', target.type, ''],
            'Текущий вес': ['change_weight', target.cur_weight, 'кг'],
            'Вес, который хотим': ['change_target', target.target_weight, 'кг'],
            'Активность': ['change_activity', target.activity, ''],
            'DCI': ['asdvsdfg', target.dci, 'кКЛ'],
        }

        for text in field.keys():
            if text == 'DCI':
                markup.add(telebot.types.InlineKeyboardButton(
                    text=f'{text} - {field[text][1]} {field[text][2]}',
                    url='https://alfagym.ru/wp-content/uploads/b/2/9/b2950dc181b1a619dc1075995da6f7f1.jpg'
                ))
            else:
                markup.add(telebot.types.InlineKeyboardButton(
                    text=f'{text} - {field[text][1]} {field[text][2]}',
                    callback_data=f'{field[text][0]}'
                ))

        markup.add(telebot.types.InlineKeyboardButton(
            text='Закрыть',
            callback_data='close'
        ))
    else:
        markup.add(telebot.types.InlineKeyboardButton(
            text=target.type,
            callback_data='my_target'
        ))
        markup.add(telebot.types.InlineKeyboardButton(
            text=f'пока не придумал',
            callback_data='hold_weight'
        ))
        markup.add(telebot.types.InlineKeyboardButton(
            text='Закрыть',
            callback_data='close'
        ))
    return markup


def cur_day_food(id, time):
    markup = telebot.types.InlineKeyboardMarkup()
    user = User.objects.get(id=id)

    cur_time = datetime.fromtimestamp(time)

    foods = user.day_food.filter(
        time__year=cur_time.year,
        time__month=cur_time.month,
        time__day=cur_time.day
    ).order_by('-time').values_list('id', 'name', 'calories', 'time')

    for id, name, calories, time in list(foods):
        if name is None:
            text = f'{time.hour:02}:{time.minute:02} - {calories}кКл'
        else:
            text = f'{time.hour:02}:{time.minute:02} - {name} {calories}кКл'

        markup.add(telebot.types.InlineKeyboardButton(
            text=text,
            callback_data=f'detail_{id}'
        ))
    markup.add(telebot.types.InlineKeyboardButton(
        text='Закрыть',
        callback_data='close'
    ))
    return markup


def detail_day_food(food_id):
    markup = telebot.types.InlineKeyboardMarkup()
    # food = UserDayFood.objects.get(id=food_id)
    # if food.name is None:
    #     markup.add(telebot.types.InlineKeyboardButton(
    #         text='Изменить',
    #         callback_data=f'change_day_dci_{food_id}'
    #     ))
    markup.add(telebot.types.InlineKeyboardButton(
        text='Изменить',
        callback_data=f'change_day_dci_{food_id}'
    ))
    markup.add(telebot.types.InlineKeyboardButton(
        text='Удалить',
        callback_data=f'delete_day_dci_{food_id}'
    ))
    markup.add(telebot.types.InlineKeyboardButton(
        text='Закрыть',
        callback_data='close'
    ))
    return markup

# def create_InlineKeyboard_programm(message):
#     markup = telebot.types.InlineKeyboardMarkup()
#     target = SqlMain.get_programm(message)
#     field = {
#         'Период': [target[0] ,'недель'],
#         'Текущая неделя': [target[1], ''],
#         'DCI на эту неделю': [target[2], 'кКл']
#     }
#     for text in field.keys():
#         markup.add(telebot.types.InlineKeyboardButton(
#             text=f'{text} - {field[text][0]} {field[text][1]}',
#             callback_data='trdfyguhij'
#         ))
#     markup.add(telebot.types.InlineKeyboardButton(
#         text='Закрыть',
#         callback_data='close'
#     ))
#     return markup


def create_keyboard_stage(id):
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    stage = SqlMain.get_stage(id)
    if stage == -1:
        return telebot.types.ReplyKeyboardRemove()
    elif stage == 0:
        keyboard.add('Мои данные', 'Сброс')
    elif stage == 1:
        keyboard.add('Мои данные', 'Моя цель', 'Сброс')
    elif stage == 2:
        keyboard.add('Мои данные', 'Моя цель', 'Сброс')
    elif stage == 3:
        keyboard.add('Мои данные', 'Моя цель', 'Мастер обучения',
                     'Начать сбор данных', 'Я знаю сколько я ем сейчас', 'Сброс')
    elif stage == 4:
        keyboard.add('Мастер обучения', 'Меню',
                     'Статистика за день', 'Мониторинг',
                     'Мои данные', 'Моя цель', 'Сброс')
    elif stage == 5:
        keyboard.add('Мои данные', 'Моя программа', 'Меню',
                     'Мастер обучения', 'Статистика за день',
                     'Статистика за неделю', 'Сброс')
    return keyboard


def create_inline_program(id):
    target = TargetUser.objects.filter(user=User.objects.get(id=id)).last()
    program = target.program
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton(
            text=f'Цель: похудеть c {target.cur_weight} кг до {target.target_weight} кг',
            callback_data='adfsgd'
        )
    )
    markup.add(
        telebot.types.InlineKeyboardButton(
            text=f'Дата начала: {program.date_start}',
            callback_data='adfsgd'
        )
    )
    # markup.add(
    #     telebot.types.InlineKeyboardButton(
    #         text=f'Рацион в начале: {program.start_dci} кКл',
    #         callback_data='adfsgd'
    #     )
    # )
    markup.add(
        telebot.types.InlineKeyboardButton(
            text=f'Норма потребления: {target.dci} кКл',
            callback_data='adfsgd'
        )
    )
    markup.add(
        telebot.types.InlineKeyboardButton(
            text=f'Фаза 1: {program.phase1} дней',
            callback_data='adfsgd'
        )
    )
    markup.add(
        telebot.types.InlineKeyboardButton(
            text=f'Фаза 2: {program.phase2} дней',
            callback_data='adfsgd'
        )
    )
    markup.add(
        telebot.types.InlineKeyboardButton(
            text=f'Прошло дней: {program.cur_day}',
            callback_data='adfsgd'
        )
    )
    markup.add(
        telebot.types.InlineKeyboardButton(
            text=f'Текущий рацион: {program.cur_dci} кКл',
            callback_data='adfsgd'
        )
    )
    markup.add(
        telebot.types.InlineKeyboardButton(
            text=f'Текущий вес: {program.cur_weight} кг',
            callback_data='adfsgd'
        )
    )
    markup.add(
        telebot.types.InlineKeyboardButton(
            text=f'Достижение цели: {program.achievement}%',
            callback_data='adfsgd'
        )
    )
    markup.add(
        telebot.types.InlineKeyboardButton(
            text='Изменить текущую цель',
            callback_data='change_cur_target'
        )
    )
    markup.add(
        telebot.types.InlineKeyboardButton(
            text='Указать текущий вес',
            callback_data='change_weight_in_program'
        )
    )
    markup.add(telebot.types.InlineKeyboardButton(
        text='Закрыть',
        callback_data='close'
    ))
    return markup


def create_inline_week_eating(id, message):
    user = User.objects.get(id=id)
    data = list(user.result_day_dci.all().order_by('-date'))
    # last_program_date = user.program.last().date_start
    # data = list(user.result_day_dci.filter(
    #     date__gte=last_program_date).order_by('-date'))
    if data:
        cur_date = datetime.fromtimestamp(message.date).date()

        if data[0].date == cur_date:
            data.pop(0)
        if len(data) > 7:
            data = data[:7]

    markup = telebot.types.InlineKeyboardMarkup()
    if data:
        for eating in data:
            markup.add(telebot.types.InlineKeyboardButton(
                text=f'{eating.date.strftime("%d:%m:%Y")} - {eating.calories}, {eating.deficit if eating.calories != 0 else "—"}',
                callback_data=f'edit_week_eating_{eating.id}'
            ))
    else:
        markup.add(telebot.types.InlineKeyboardButton(
            text='У вас нет других приемов пищи',
            callback_data='adfsgd'
        ))
    markup.add(telebot.types.InlineKeyboardButton(
        text='Закрыть',
        callback_data='close'
    ))
    return markup


def last_message(mesKey):
    markup = telebot.types.InlineKeyboardMarkup()
    if mesKey == 'start_last':
        markup.add(telebot.types.InlineKeyboardButton(
            text='Начать работу',
            callback_data='login'
        ))
    elif mesKey == 'stage1_last':
        markup.add(telebot.types.InlineKeyboardButton(
            text='Создать цель',
            callback_data='create_target'
        ))
    elif mesKey == 'stage2_last':
        markup.add(telebot.types.InlineKeyboardButton(
            text='Начать обучение',
            callback_data='start_guide'
        ))
        markup.add(telebot.types.InlineKeyboardButton(
            text='Перейти на следующий уровень',
            callback_data='skip_guide'
        ))
    elif mesKey == 'stage3_last':
        markup.add(telebot.types.InlineKeyboardButton(
            text='Начать сбор данных',
            callback_data='start_get_cur_DCI'
        ))
        markup.add(telebot.types.InlineKeyboardButton(
            text='Я знаю сколько я ем сейчас',
            callback_data='get_cur_DCI'
        ))
    return markup
