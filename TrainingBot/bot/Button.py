from django.db.models import Sum
from django.forms import model_to_dict
import statistics
from datetime import datetime, date, timedelta
import telebot
import bot.InlineKeyboard as InlineKeyboard
import bot.SqlMain as SqlMain
from bot.config import ACTIVITY, TYPE, TOKEN, K_PHASE2

from model.models import *


bot = telebot.TeleBot(TOKEN)


def check_int(x):
    try:
        y = int(x)
        return True
    except:
        return False


def check_float(x):
    try:
        y = float(x)
        return True
    except:
        return False


def change_DCI_ideal_weight(message):
    if message.from_user.is_bot:
        id = message.chat.id
    else:
        id = message.from_user.id

    user = User.objects.get(id=id)
    info_user = user.info.last()
    target_user = user.target.last()
    inf = (
        info_user.age,
        info_user.height,
        target_user.cur_weight,
        info_user.gender,
        target_user.activity
    )
    print(inf)
    if (None not in inf) and ('None' not in inf):
        if inf[3] == 'woomen':
            DCI = int(
                (655 + (9.6 * inf[2]) + (1.8 * inf[1]) - (4.7 * inf[0])) * ACTIVITY.get(inf[4]))
        else:
            DCI = int(
                (66 + (13.7 * inf[2]) + (5 * inf[1]) - (6.8 * inf[0])) * ACTIVITY.get(inf[4]))

        target_user = TargetUser.objects.get(user=id)
        target_user.dci = DCI
        target_user.save()

    if inf[3] != 'None' and inf[1] != 0:
        if inf[3] == 'woomen':
            ideal_weight = (3.5 * inf[1] / 2.54 - 108) * 0.453
        else:
            ideal_weight = (4 * inf[1] / 2.54 - 128) * 0.453

        info_user = InfoUser.objects.get(user=id)
        info_user.ideal_weight = round(ideal_weight, 1)
        info_user.save()


def change_info(message, field):
    if message.from_user.is_bot:
        id = message.chat.id
    else:
        id = message.from_user.id
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(
        text='Попробовать снова',
        callback_data='my_info'
    ))

    if not check_int(message.text):
        bot.send_message(
            chat_id=message.chat.id,
            text='Вводите целое число, повторите попытку',
            reply_markup=markup
        )
        return
    if int(message.text) < 0:
        bot.send_message(
            chat_id=id,
            text='Вводите положительное число, повторите попытку',
            reply_markup=markup
        )
        return

    info_user = InfoUser.objects.get(user=id)
    if field == 'age':
        info_user.age = int(message.text)
    elif field == 'height':
        info_user.height = int(message.text)
    info_user.save()

    change_DCI_ideal_weight(message)

    bot.send_message(
        chat_id=id,
        text='Укажите следующие данные',
        reply_markup=InlineKeyboard.create_InlineKeyboard_user_info(message)
    )

    info_user = InfoUser.objects.get(user=id)

    if all([info_user.age, info_user.height]) and info_user.gender != 'None' and SqlMain.get_stage(id) == 0:
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton(
            text='Создать цель',
            callback_data='create_target'
        ))
        user_stage_guide = UserStageGuide.objects.get(user=id)
        user_stage_guide.stage = 1
        user_stage_guide.save()

        bot.send_message(
            chat_id=id,
            text='Отлично, теперь мы знаем о вас немного больше.',
            reply_markup=InlineKeyboard.create_keyboard_stage(id)
        )
        bot.send_message(
            chat_id=id,
            text=('Далее вам необходимо понять к чему вы стремитесь. '
                  'Создайте свою первую цель, и мы поможем ее достигнуть.'),
            reply_markup=markup
        )


# def change_weight(message):
#     markup = telebot.types.InlineKeyboardMarkup()
#     markup.add(telebot.types.InlineKeyboardButton(
#         text='Попробовать снова',
#         callback_data='Сбросить вес'
#     ))
#     if not check_float(message.text):
#         bot.send_message(
#             chat_id=message.chat.id,
#             text='Вводите целое или дробное число, повторите попытку',
#             reply_markup=markup
#         )
#         return
#     if float(message.text) < 0:
#         bot.send_message(
#             chat_id=message.chat.id,
#             text='Вводите положительное число, повторите попытку',
#             reply_markup=markup
#         )
#         return

#     data = (round(float(message.text), 1), message.from_user.id)

#     request = f'''UPDATE target_user SET cur_weight = ? WHERE user = ?'''
#     cur.execute(request, data)
#     con.commit()

#     change_DCI_ideal_weight(message)

#     bot.send_message(
#         chat_id=message.chat.id,
#         text='Давайте выберем, что вы хотите',
#         reply_markup=InlineKeyboard.create_InlineKeyboard_target(message, False)
#     )


def change_target_weight(message, field):
    id = message.from_user.id
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(
        text='Попробовать снова',
        callback_data=TYPE[1]
    ))
    if not check_float(message.text):
        bot.send_message(
            chat_id=message.chat.id,
            text='Вводите целое или дробное число, повторите попытку',
            reply_markup=markup
        )
        return
    if float(message.text) < 0:
        bot.send_message(
            chat_id=message.chat.id,
            text='Вводите положительное число, повторите попытку',
            reply_markup=markup
        )
        return

    target_user = TargetUser.objects.filter(user=id).last()
    if field == 'target_weight':
        target_user.target_weight = round(float(message.text), 1)
    elif field == 'cur_weight':
        target_user.cur_weight = round(float(message.text), 1)
    target_user.save()

    change_DCI_ideal_weight(message)

    markup = InlineKeyboard.create_InlineKeyboard_target(message, False)
    bot.send_message(
        chat_id=id,
        text='Укажите следующие данные',
        reply_markup=markup
    )

    target_user = TargetUser.objects.filter(user=id).last()

    if (all([target_user.cur_weight, target_user.target_weight])
        and ('None' not in (target_user.type, target_user.activity))
            and SqlMain.get_stage(id) == 1):

        keyboard = telebot.types.ReplyKeyboardMarkup(True)
        markup = telebot.types.InlineKeyboardMarkup()

        markup.add(telebot.types.InlineKeyboardButton(
            text='Начать обучение',
            callback_data='start_guide'
        ))
        markup.add(telebot.types.InlineKeyboardButton(
            text='Перейти на следующий уровень',
            callback_data='skip_guide'
        ))

        keyboard.add('Мои данные', 'Моя цель')
        user_stage_guide = UserStageGuide.objects.get(user=id)
        user_stage_guide.stage = 2
        user_stage_guide.save()

        bot.send_message(
            chat_id=id,
            text=('Отлично, цель поставлена и она вполне достижима. '
                  'Теперь нам надо создать программу управления весом, '
                  'которая позволит каждый контролировать ваш рацион '
                  'и приближать поставленную цель.'),
            reply_markup=keyboard
        )
        bot.send_message(
            chat_id=id,
            text=('Перед тем как продолжить '
                  'Вам необходимо пройти курс молодого бойца, '
                  'который позволит без проблем определять количество калорий в каждом блюде. '
                  'Если вы уже все умеете то курс можно пропустить и '
                  'сразу перейти на следующий уровень.'),
            reply_markup=markup
        )


def change_cur_DCI(message):
    if message.from_user.is_bot:
        id = message.chat.id
    else:
        id = message.from_user.id

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(
        text='Попробовать снова',
        callback_data='get_cur_DCI'
    ))
    if not check_int(message.text):
        bot.send_message(
            chat_id=id,
            text='Вводите целое число, повторите попытку',
            reply_markup=markup
        )
        return
    if int(message.text) < 0:
        bot.send_message(
            chat_id=id,
            text='Вводите положительное число, повторите попытку',
            reply_markup=markup
        )
        return

    target_user = TargetUser.objects.filter(user=id).last()
    target_user.cur_dci = int(message.text)
    target_user.save()

    if SqlMain.get_stage(id) == 3 or SqlMain.get_stage(id) == 4:
        update_stage_5(id, message)
        return
    bot.send_message(
        chat_id=id,
        text='Вы изменили текущий DCI'
    )


def update_result_day_DCI(message):
    if message.from_user.is_bot:
        id = message.chat.id
    else:
        id = message.from_user.id

    cur_time = datetime.fromtimestamp(message.date)
    user = User.objects.get(id=id)

    calories = user.day_food.filter(
        time__year=cur_time.year,
        time__month=cur_time.month,
        time__day=cur_time.day
    ).aggregate(Sum('calories'))

    if calories.get('calories__sum') is None:
        calories['calories__sum'] = 0

    cur_date = date(cur_time.year, cur_time.month, cur_time.day)
    if not ResultDayDci.objects.filter(
        user=user,
        date=cur_date
    ).exists():
        result_dci = ResultDayDci(
            user=user,
            date=cur_date
        )
        result_dci.save()
    else:
        result_dci = ResultDayDci.objects.get(
            user=user,
            date=cur_date
        )

    result_dci.calories = calories.get('calories__sum')
    result_dci.save()

    if SqlMain.get_stage(id) == 4:
        print('-----------------------')
        tmp_res = check_variance(id)
        if tmp_res[0]:
            target_user = TargetUser.objects.filter(user=id).last()
            target_user.cur_dci = tmp_res[1]
            target_user.save()
            print('dci определено')
            return 'dci_success'
        print('-----------------------')
    return result_dci.calories


def add_from_menu_day_DCI(call):
    # if change:
    # user = User.objects.get(id=call)
    # calories = user.day_food.all().aggregate(Sum('calories'))

    # target_user = TargetUser.objects.get(user=call)
    # target_user.cur_day_dci = calories.get('calories__sum')
    # target_user.save()
    # return

    # if delete:
    # food = UserDayFood.objects.get(id=call)
    # calories = food.calories
    # food.delete()

    # target_user = TargetUser.objects.get(user=flag)
    # target_user.cur_day_dci = target_user.cur_day_dci - calories
    # target_user.save()

    # bot.send_message(
    #     chat_id=flag,
    #     text=f'Вы удалили {calories}кКл'
    # )
    # bot.send_message(
    #     chat_id=flag,
    #     text=f'Сегодня вы поели на {target_user.cur_day_dci}',
    #     reply_markup=InlineKeyboard.cur_day_food(flag)
    # )
    # return

    name = None
    msg = call.data[5:]
    name, calories = msg.split('_')
    if name == 'None':
        name = None
    data = (int(calories), call.message.chat.id, call.message.date)

    food_user = UserDayFood(
        user=User.objects.get(id=data[1]),
        name=name,
        calories=data[0],
        time=datetime.fromtimestamp(data[2])
    )
    food_user.save()

    calories = update_result_day_DCI(call.message)
    if calories == 'dci_success':
        update_stage_5(data[1], call.message)
        return

    text = f'{name} - {data[0]}' if not name is None else f'{data[0]}'
    bot.send_message(
        chat_id=data[1],
        text=text
    )
    bot.send_message(
        chat_id=data[1],
        text=f'Вы сегодня поели на {calories} кКл'
    )


def detail_food(food_id):
    food = UserDayFood.objects.get(id=food_id)
    print(food.time)
    if food.name is None:
        text = f'{food.time.hour}:{food.time.minute} - {food.calories}кКл'
    else:
        text = f'{food.time.hour}:{food.time.minute} - {food.name} {food.calories}кКл'

    bot.send_message(
        chat_id=food.user.id,
        text=text,
        reply_markup=InlineKeyboard.detail_day_food(food_id)
    )


def change_day_DCI(message, food_id):
    if message.from_user.is_bot:
        id = message.chat.id
    else:
        id = message.from_user.id

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(
        text='Попробовать снова',
        callback_data=f'detail_{food_id}'
    ))
    food = UserDayFood.objects.get(id=food_id)

    tmp = message.text.split()
    print(tmp)

    if not check_int(tmp[0]):
        bot.send_message(
            chat_id=id,
            text='Вводите целое число, повторите попытку',
            reply_markup=markup
        )
        return
    if int(tmp[0]) < 0:
        bot.send_message(
            chat_id=id,
            text='Вводите положительное число, повторите попытку',
            reply_markup=markup
        )
        return
    food.calories = int(tmp[0])
    if len(tmp) > 1:
        food.name = ' '.join(tmp[1:])

    food.save()

    # user = User.objects.get(id=id)
    # calories = user.day_food.all().aggregate(Sum('calories'))

    # result_dci, _ = ResultDayDci.objects.get_or_create(
    #     user=id,
    #     time=datetime.fromtimestamp(message.date)
    # )
    # result_dci.calories = calories.get('calories__sum')
    # result_dci.save()
    calories = update_result_day_DCI(message)
    if calories == 'dci_success':
        update_stage_5(id, message)
        return

    bot.send_message(
        chat_id=id,
        text='Вы изменили данные'
    )

    bot.send_message(
        chat_id=id,
        text=f'Сегодня вы поели на {calories}',
        reply_markup=InlineKeyboard.cur_day_food(id, message.date)
    )


def week_eating(message, eating_id):
    if message.from_user.is_bot:
        id = message.chat.id
    else:
        id = message.from_user.id

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(
        text='Попробовать снова',
        callback_data='week_eating'
    ))
    eating = ResultDayDci.objects.get(id=eating_id)

    if not check_int(message.text):
        bot.send_message(
            chat_id=id,
            text='Вводите целое число, повторите попытку',
            reply_markup=markup
        )
        return
    if int(message.text) < 0:
        bot.send_message(
            chat_id=id,
            text='Вводите положительное число, повторите попытку',
            reply_markup=markup
        )
        return
    eating.calories = int(message.text)
    eating.save()

    # user = User.objects.get(id=id)
    # calories = user.day_food.all().aggregate(Sum('calories'))

    # result_dci, _ = ResultDayDci.objects.get_or_create(
    #     user=id,
    #     time=datetime.fromtimestamp(message.date)
    # )
    # result_dci.calories = calories.get('calories__sum')
    # result_dci.save()

    bot.send_message(
        chat_id=id,
        text='Приемы пищи за последние 7 дней',
        reply_markup=InlineKeyboard.create_inline_week_eating(id, message)
    )


def delete_day_DCI(message, food_id):
    if message.from_user.is_bot:
        id = message.chat.id
    else:
        id = message.from_user.id

    food = UserDayFood.objects.get(id=food_id)
    cal_delete = food.calories
    food.delete()

    calories = update_result_day_DCI(message)
    if calories == 'dci_success':
        update_stage_5(id, message)
        return

    bot.send_message(
        chat_id=id,
        text=f'Вы удалили {cal_delete}кКл'
    )
    bot.send_message(
        chat_id=id,
        text=f'Сегодня вы поели на {calories}',
        reply_markup=InlineKeyboard.cur_day_food(id, message.date)
    )


def create_data_to_analise(id):
    data = list(ResultDayDci.objects.filter(user=id).order_by(
        'date').values_list('calories', 'date'))
    if len(data) < 5:
        return False

    calories = [x[0] for x in data[1:-1]]
    date = [x[1] for x in data[1:-1]]
    res_calories = []

    for index in range(len(date)-1):
        res_calories.append(calories[index])
        days_delta = date[index+1] - date[index]
        if days_delta != timedelta(days=1):
            res_calories.extend([0]*(days_delta.days-1))

    res_calories.append(calories[-1])
    print(res_calories)
    return res_calories


def analise_data(data):
    # result = False
    # for index in range(len(data)-3):
    #     cound_right_deviation = 0
    #     tmp_data = data[index:index+4]
    #     print(tmp_data)
    #     for index_el in range(len(tmp_data)-1):
    #         if not any([tmp_data[index_el], tmp_data[index_el+1]]):
    #             cound_right_deviation = 0
    #             break
    #         deviation = lambda i: abs(tmp_data[index_el] - tmp_data[index_el+i]) / max((tmp_data[index_el], tmp_data[index_el+i]))
    #         if deviation(1) <= 0.2:
    #             cound_right_deviation += 1
    #         elif (index_el != len(tmp_data) - 2) and (deviation(2) <= 0.2):
    #             cound_right_deviation += 1

    #     if cound_right_deviation >= 2:
    #         result = True
    #         print('данные подходят')
    # return result
    result = []
    zeroDaysCount = 0
    tmpPrev = 0
    for i in range(len(data)):
        current = data[i]
        if len(result) > 0:
            prev = result[-1]
            if current != 0 and abs(1 - prev / current) <= 0.2:
                result.append(current)
            else:
                if zeroDaysCount == 0:
                    tmpPrev = current
                    zeroDaysCount += 1
                else:
                    zeroDaysCount = 0
                    result.clear()
                    if current != 0 and abs(1 - tmpPrev / current) <= 0.2:
                        result.append(tmpPrev)
                    result.append(current)
        else:
            result.append(current)
        if len(result) - result.count(0) >= 3:
            break
    if len(result) - result.count(0) >= 3:
        print('--------------')
        print(result)
        print('--------------')
        return (True, int(sum(result)/len(result)))
    return (False, None)


def check_variance(id):
    data = create_data_to_analise(id)
    if not data:
        print('мало данных')
        return (False, None)

    return analise_data(data)
    # flg_day_skip = False
    # days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    # data = list(ResultDayDci.objects.filter(user=id).order_by('time').values_list('calories', 'time'))
    # calories = [x[0] for x in data]
    # time = [x[1] for x in data]

    # if len(data) < 5:
    #     print('мало данных')
    #     return False

    # res_time = [(el.month, el.day) for el in time[-4:-1]]
    # print(time)
    # print(res_time)
    # for index, (month, day) in enumerate(res_time[:-1], 0):
    #     if day == days[month-1]:
    #         fday = 1
    #         fmh = month+1
    #     else:
    #         fday = day + 1
    #         fmh = month
    #     if res_time[index+1][1] == fday and res_time[index+1][0] == fmh:
    #         continue
    #     elif res_time[index+1][1] == fday + 1 and res_time[index+1][0] == fmh:
    #         if flg_day_skip:
    #             print('пропущено более одного дня')
    #             return False
    #         flg_day_skip = True
    #         continue
    #     else:
    #         print('даты не прошли')
    #         return False

    # print('даты прошли')

    # res_calories = statistics.stdev(calories[-4:-1]) / statistics.mean(calories[-4:-1]) * 100

    # print('res_calories =', res_calories)
    # if not (res_calories <= 20):
    #     return False
    # return True

    # result = False
    # days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    # data = list(ResultDayDci.objects.filter(user=id).order_by('date').values_list('calories', 'date'))

    # if len(data) < 5:
    #     print('мало данных')
    #     return False

    # calories = [x[0] for x in data]
    # time = [x[1] for x in data]
    # print(calories)
    # print('Исходные данные:')
    # print(calories[1:-1])
    # print(time[1:-1])
    # print('-------------------')
    # for index in range(len(calories[1:-1])-2):
    #     flag_20 = True # 300 350 100 350 350 100 350 350 100
    #     flag_date = True
    #     flag_day_skip = False
    #     tmp_calories = calories[1:-1][index:index+3]
    #     tmp_time = [(el.month, el.day) for el in time[1:-1][index:index+3]]

    #     print(tmp_calories)
    #     print(tmp_time)

    #     for index_el in range(len(tmp_calories)-1):
    #         if not any([tmp_calories[index_el], tmp_calories[index_el+1]]):
    #             flag_20 = False
    #             break
    #         print(abs(tmp_calories[index_el] - tmp_calories[index_el+1]) / max((tmp_calories[index_el], tmp_calories[index_el+1])))
    #         if not (abs(tmp_calories[index_el] - tmp_calories[index_el+1]) / max((tmp_calories[index_el], tmp_calories[index_el+1])) <= 0.2):
    #             print('большая разница')
    #             flag_20 = False
    #             break

    #         day = tmp_time[index_el][1]
    #         month = tmp_time[index_el][0]
    #         if day == days[month-1]:
    #             fday = 1
    #             fmh = month+1
    #         else:
    #             fday = day + 1
    #             fmh = month
    #         if tmp_time[index_el+1][1] == fday and tmp_time[index_el+1][0] == fmh:
    #             continue
    #         elif tmp_time[index_el+1][1] == fday + 1 and tmp_time[index_el+1][0] == fmh:
    #             if flag_day_skip:
    #                 print('пропущено более одного дня')
    #                 flag_date = False
    #                 break
    #             flag_day_skip = True
    #             continue
    #         else:
    #             print('даты не прошли')
    #             flag_date = False
    #             break

    #     if flag_20 and flag_date:
    #         print('это подходящие данные')
    #         print('-------------------')
    #         result = True

    # return result


def update_stage_3(id):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(
        text='Начать сбор данных',
        callback_data='start_get_cur_DCI'
    ))
    markup.add(telebot.types.InlineKeyboardButton(
        text='Я знаю сколько я ем сейчас',
        callback_data='get_cur_DCI'
    ))
    user_stage_guide = UserStageGuide.objects.get(user=id)
    user_stage_guide.stage = 3
    user_stage_guide.save()

    bot.send_message(
        chat_id=id,
        text='Теперь вы умеете считать калории и определять сколько вы съели в течение дня',
        reply_markup=InlineKeyboard.create_keyboard_stage(id)
    )
    bot.send_message(
        chat_id=id,
        text=(
            'Настало время определить сколько калорий вы '
            'съедаете сейчас. Для этого просто фиксируйте в приложении '
            'каждый прием пищи. Если вы уже знаете сколько едите сейчас, '
            'то данный шаг можно пропустить.'
        ),
        reply_markup=markup
    )


def update_stage_4(id):
    user_stage_guide = UserStageGuide.objects.get(user=id)
    user_stage_guide.stage = 4
    user_stage_guide.save()

    bot.send_message(
        chat_id=id,
        text='Начинаем фиксировать данные, не забывайте фиксировать каждый прием пищи.',
        reply_markup=InlineKeyboard.create_keyboard_stage(id)
    )


def update_stage_5(id, message):
    user_stage_guide = UserStageGuide.objects.get(user=id)
    user_stage_guide.stage = 5
    user_stage_guide.save()

    create_program(id, message)

    bot.send_message(
        chat_id=id,
        text=('Теперь у нас достаточно данных чтобы рассчитать '
              'для вас максимально эффективную программу '
              'управления весом.'),
        reply_markup=InlineKeyboard.create_keyboard_stage(id)
    )
    bot.send_message(
        chat_id=id,
        text=('Программа состоит из двух фаз. Фаза 1 - снижаем '
              'калории до правильного уровня в соответсвии с '
              'вашим образом жизни. Фаза 2 - вводим небольшой '
              'дефицит калорий, для начала процесса похудения.'),
    )
    bot.send_message(
        chat_id=id,
        text=('Ваша программа и текущие показатели всегда доступны '
              'по кнопке "Программа" в основном меню приложения.'),
        reply_markup=InlineKeyboard.create_inline_program(id)
    )


def create_program(id, message):
    cur_time = datetime.fromtimestamp(message.date)
    cur_date = date(cur_time.year, cur_time.month, cur_time.day)

    target = TargetUser.objects.filter(user=id).last()
    cur_dci = target.cur_dci
    dci = target.dci
    cur_weight = target.cur_weight
    target_weight = target.target_weight

    program = UserProgram(
        user=User.objects.get(id=id),
        date_start=cur_date,
        start_dci=cur_dci,
        cur_dci=cur_dci,
        phase1=int((cur_dci - dci) / 100 * 7)+1 if (cur_dci - dci) > 0 else 0,
        phase2=(6000 * (cur_weight - target_weight) / 200
                / K_PHASE2) if (cur_weight - target_weight) > 0 else 0,
        cur_day=1,
        cur_weight=cur_weight,
        achievement=0
    )
    program.save()

    target.program = program
    target.save()


def change_weight_in_program(message):
    if message.from_user.is_bot:
        id = message.chat.id
    else:
        id = message.from_user.id
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(
        text='Попробовать снова',
        callback_data='program'
    ))

    if not check_float(message.text):
        bot.send_message(
            chat_id=message.chat.id,
            text='Вводите целое или дробное число, повторите попытку',
            reply_markup=markup
        )
        return
    if float(message.text) < 0:
        bot.send_message(
            chat_id=message.chat.id,
            text='Вводите положительное число, повторите попытку',
            reply_markup=markup
        )
        return
    user = User.objects.get(id=id)
    target_user = user.target.last()
    # target_user = TargetUser.objects.filter(user=user).last()
    program_user = target_user.program
    program_user.cur_weight = round(float(message.text), 1)
    program_user.achievement = int((
        1 - (target_user.cur_weight - program_user.cur_weight) /
        (target_user.cur_weight - target_user.target_weight)
    ) * 100)
    program_user.save()

    cur_time = datetime.fromtimestamp(message.date)
    cur_date = date(cur_time.year, cur_time.month, cur_time.day)

    day_result, _ = ResultDayDci.objects.get_or_create(
        user=user,
        date=cur_date
    )
    day_result.cur_weight = round(float(message.text), 1)
    day_result.save()
    bot.send_message(
        chat_id=id,
        text=('Ваша программа и текущие показатели всегда доступны '
              'по кнопке "Программа" в основном меню приложения.'),
        reply_markup=InlineKeyboard.create_inline_program(id)
    )


def change_cur_target(message):
    if message.from_user.is_bot:
        id = message.chat.id
    else:
        id = message.from_user.id

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(
        text='Попробовать снова',
        callback_data='program'
    ))

    if not check_float(message.text):
        bot.send_message(
            chat_id=message.chat.id,
            text='Вводите целое или дробное число, повторите попытку',
            reply_markup=markup
        )
        return
    if float(message.text) < 0:
        bot.send_message(
            chat_id=message.chat.id,
            text='Вводите положительное число, повторите попытку',
            reply_markup=markup
        )
        return

    user = User.objects.get(id=id)
    cur_target = TargetUser.objects.filter(
        user=user).last()

    kwargs = model_to_dict(cur_target, exclude=['id', 'user', 'program'])
    new_target = TargetUser(**kwargs)
    new_target.user = user
    new_target.target_weight = round(float(message.text), 1)
    new_target.save()

    create_program(id, message)

    bot.send_message(
        chat_id=id,
        text=('Ваша программа и текущие показатели всегда доступны '
              'по кнопке "Программа" в основном меню приложения.'),
        reply_markup=InlineKeyboard.create_inline_program(id)
    )
