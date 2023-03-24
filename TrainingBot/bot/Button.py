from django.db.models import Sum
from django.forms import model_to_dict
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, date, timedelta
import telebot
import bot.InlineKeyboard as InlineKeyboard
import bot.SqlMain as SqlMain
from bot.SendMessage import template_send_message
from bot.config import *
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
    if (None not in inf) and ('None' not in inf):
        DCI = get_ideal_DCI(inf)
        target_user.dci = DCI
        target_user.save()

    if inf[3] != 'None' and inf[1] != 0:
        if inf[3] == 'woomen':
            ideal_weight = (3.5 * inf[1] / 2.54 - 108) * 0.453
        else:
            ideal_weight = (4 * inf[1] / 2.54 - 128) * 0.453

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

    if (all([info_user.age, info_user.height])
        and info_user.gender != 'None'
            and SqlMain.get_stage(id) == 0):
        update_stage_1(id)


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

    if (all([target_user.cur_weight, target_user.target_weight])
        and ('None' not in (target_user.type, target_user.activity))
            and SqlMain.get_stage(id) == 1):
        update_stage_2(id)


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
    remind = user.remind.last()

    calories = user.day_food.filter(
        time__year=cur_time.year,
        time__month=cur_time.month,
        time__day=cur_time.day
    ).aggregate(Sum('calories'))

    if calories.get('calories__sum') is None:
        calories['calories__sum'] = 0

    if calories != 0:
        remind.remind_first = False
        remind.save()
    cur_date = date(cur_time.year, cur_time.month, cur_time.day)

    user_program = user.program.last()
    user_target = user.target.last()
    if SqlMain.get_stage(id) == 5:

        if calories.get('calories__sum') > user_program.cur_dci / 2:
            remind.remind_second = False
            remind.save()

        if len(user.result_day_dci.filter(date=cur_date)) == 0 and user_program.date_start != cur_date:
            user_program.cur_day += 1
            user_program.save()

        dci = user.target.last().dci

        if ((user_program.cur_day - user_program.phase1) == 1
                and user_program.cur_dci != int(dci * (1 - user_target.percentage_decrease / 100))):
            user_program.cur_dci = get_normal_dci(
                id, user_program.phase1, user_program.cur_day)
            user_program.save()
        else:
            if (user_program.cur_day % 7 == 1
                    and len(user.result_day_dci.filter(date=cur_date)) == 0
                    and user_program.cur_day != 1
                    and user_program.phase1 != 0):
                user_program.cur_dci = get_normal_dci(
                    id, user_program.phase1, user_program.cur_day)
                user_program.save()

                if user_program.cur_dci < dci:
                    user_program.cur_dci = dci
                    user_program.save()

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

    if SqlMain.get_stage(id) == 4:
        norm = user_target.dci
    else:
        if user_program.cur_day > user_program.phase1:
            norm = user_target.dci
        else:
            norm = user_program.cur_dci
    result_dci.calories = calories.get('calories__sum')
    result_dci.deficit = norm - calories.get('calories__sum')
    result_dci.save()

    if SqlMain.get_stage(id) == 4:
        tmp_res = check_variance(id)
        if tmp_res[0]:
            target_user = TargetUser.objects.filter(user=id).last()
            target_user.cur_dci = tmp_res[1]
            target_user.save()
            print('dci определено')
            return 'dci_success'
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

    text = create_text_stage_4_5(calories, data[1])
    bot.send_message(
        chat_id=data[1],
        text=text
    )
    send_yesterday_remind(data[1], call.message)


def detail_food(food_id, user_id):
    try:
        food = UserDayFood.objects.get(id=food_id)
        if food.name is None:
            text = f'{food.time.hour}:{food.time.minute} - {food.calories}кКл'
        else:
            text = f'{food.time.hour}:{food.time.minute} - {food.name} {food.calories}кКл'

        bot.send_message(
            chat_id=food.user.id,
            text=text,
            reply_markup=InlineKeyboard.detail_day_food(food_id)
        )
    except ObjectDoesNotExist:
        bot.send_message(
            chat_id=user_id,
            text='Запись была удалена'
        )
    except Exception:
        bot.send_message(
            chat_id=user_id,
            text='Неизвестная ошибка'
        )


def change_day_DCI(message, food_id):
    try:
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

        text = create_text_days_eating(calories, id)

        bot.send_message(
            chat_id=id,
            text=text,
            reply_markup=InlineKeyboard.cur_day_food(id, message.date)
        )
    except ObjectDoesNotExist:
        bot.send_message(
            chat_id=id,
            text='Запись была удалена'
        )
    except Exception:
        bot.send_message(
            chat_id=id,
            text='Неизвестная ошибка'
        )


def week_eating(message, eating_id):
    try:
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

        eating.deficit += eating.calories - int(message.text)
        eating.calories = int(message.text)
        eating.save()

        bot.send_message(
            chat_id=id,
            text='Приемы пищи за последние 7 дней',
            reply_markup=InlineKeyboard.create_inline_week_eating(id, message)
        )
    except ObjectDoesNotExist:
        bot.send_message(
            chat_id=id,
            text='Запись была удалена',
        )
    except Exception:
        bot.send_message(
            chat_id=id,
            text='Неизвестная ошибка'
        )


def delete_day_DCI(message, food_id):
    try:
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
        text = create_text_days_eating(calories, id)
        bot.send_message(
            chat_id=id,
            text=text,
            reply_markup=InlineKeyboard.cur_day_food(id, message.date)
        )
    except ObjectDoesNotExist:
        bot.send_message(
            chat_id=id,
            text='Запись была удалена'
        )
    except Exception:
        bot.send_message(
            chat_id=id,
            text='Неизвестная ошибка'
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
        return (True, int(sum(result)/len(result)))
    return (False, None)


def check_variance(id):
    data = create_data_to_analise(id)
    if not data:
        print('мало данных')
        return (False, None)

    return analise_data(data)


def update_stage_1(id):
    # markup = telebot.types.InlineKeyboardMarkup()
    # markup.add(telebot.types.InlineKeyboardButton(
    #     text='Создать цель',
    #     callback_data='create_target'
    # ))
    user_stage_guide = UserStageGuide.objects.get(user=id)
    user_stage_guide.stage = 1
    user_stage_guide.save()

    template_send_message(bot, id, 'stage1')
    # bot.send_message(
    #     chat_id=id,
    #     text='Отлично, теперь мы знаем о вас немного больше.',
    #     reply_markup=InlineKeyboard.create_keyboard_stage(id)
    # )
    template_send_message(bot, id, 'stage1_last')
    # bot.send_message(
    #     chat_id=id,
    #     text=('Далее вам необходимо понять к чему вы стремитесь. '
    #           'Создайте свою первую цель, и мы поможем ее достигнуть.'),
    #     reply_markup=markup
    # )


def update_stage_2(id):
    user_stage_guide = UserStageGuide.objects.get(user=id)
    user_stage_guide.stage = 2
    user_stage_guide.save()

    template_send_message(bot, id, 'stage2')
    # bot.send_message(
    #     chat_id=id,
    #     text=('Отлично, цель поставлена и она вполне достижима. '
    #           'Теперь нам надо создать программу управления весом, '
    #           'которая позволит каждый контролировать ваш рацион '
    #           'и приближать поставленную цель.'),
    #     reply_markup=keyboard
    # )
    template_send_message(bot, id, 'stage2_last')
    # bot.send_message(
    #     chat_id=id,
    #     text=('Перед тем как продолжить '
    #           'Вам необходимо пройти курс молодого бойца, '
    #           'который позволит без проблем определять количество калорий в каждом блюде. '
    #           'Если вы уже все умеете то курс можно пропустить и '
    #           'сразу перейти на следующий уровень.'),
    #     reply_markup=markup
    # )


def update_stage_3(id):
    # markup = telebot.types.InlineKeyboardMarkup()
    # markup.add(telebot.types.InlineKeyboardButton(
    #     text='Начать сбор данных',
    #     callback_data='start_get_cur_DCI'
    # ))
    # markup.add(telebot.types.InlineKeyboardButton(
    #     text='Я знаю сколько я ем сейчас',
    #     callback_data='get_cur_DCI'
    # ))
    user_stage_guide = UserStageGuide.objects.get(user=id)
    user_stage_guide.stage = 3
    user_stage_guide.save()

    template_send_message(bot, id, 'stage3')
    # bot.send_message(
    #     chat_id=id,
    #     text='Теперь вы умеете считать калории и определять сколько вы съели в течение дня',
    #     reply_markup=InlineKeyboard.create_keyboard_stage(id)
    # )
    template_send_message(bot, id, 'stage3_last')
    # bot.send_message(
    #     chat_id=id,
    #     text=(
    #         'Настало время определить сколько калорий вы '
    #         'съедаете сейчас. Для этого просто фиксируйте в приложении '
    #         'каждый прием пищи. Если вы уже знаете сколько едите сейчас, '
    #         'то данный шаг можно пропустить.'
    #     ),
    #     reply_markup=markup
    # )


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

    template_send_message(bot, id, 'stage5')
    # bot.send_message(
    #     chat_id=id,
    #     text=('Теперь у нас достаточно данных чтобы рассчитать '
    #           'для вас максимально эффективную программу '
    #           'управления весом.'),
    #     reply_markup=InlineKeyboard.create_keyboard_stage(id)
    # )
    # bot.send_message(
    #     chat_id=id,
    #     text=('Программа состоит из двух фаз. Фаза 1 - снижаем '
    #           'калории до правильного уровня в соответсвии с '
    #           'вашим образом жизни. Фаза 2 - вводим небольшой '
    #           'дефицит калорий, для начала процесса похудения.'),
    # )
    bot.send_message(
        chat_id=id,
        text='Ваша программа',
        reply_markup=InlineKeyboard.create_inline_program(id)
    )


def create_program(id, message):
    cur_time = datetime.fromtimestamp(message.date)
    cur_date = date(cur_time.year, cur_time.month, cur_time.day)

    user = User.objects.get(id=id)
    target = user.target.last()
    cur_dci = target.cur_dci
    dci = target.dci
    cur_weight = target.cur_weight
    target_weight = target.target_weight

    phase1 = (int((cur_dci - dci) / 100) + 1) * 7 if (cur_dci - dci) > 0 else 0
    phase2 = (6000 * (cur_weight - target_weight) / 200 /
              K_PHASE2) if (cur_weight - target_weight) > 0 else 0
    cur_dci_tmp = 0
    if phase1 == 0:
        cur_dci_tmp = dci * (1 - target.percentage_decrease / 100)
    elif (cur_dci - dci) > 100:
        cur_dci_tmp = cur_dci - 100
    else:
        cur_dci_tmp = dci

    program = UserProgram(
        user=user,
        date_start=cur_date,
        start_dci=cur_dci,
        cur_dci=cur_dci_tmp,
        phase1=phase1,
        phase2=phase2,
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

    program_user = target_user.program
    program_user.cur_weight = round(float(message.text), 1)
    program_user.achievement = int((
        (target_user.cur_weight - program_user.cur_weight) /
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
        text='Ваша программа',
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
    cur_target = user.target.last()

    kwargs = model_to_dict(
        cur_target,
        exclude=['id', 'user', 'program']
    )
    new_target = TargetUser(**kwargs)
    new_target.user = user
    new_target.target_weight = round(float(message.text), 1)
    new_target.save()

    create_program(id, message)

    bot.send_message(
        chat_id=id,
        text=('Ваша программа'),
        reply_markup=InlineKeyboard.create_inline_program(id)
    )


def get_normal_dci(id, phase1, cur_day):
    user = User.objects.get(id=id)
    user_target = user.target.last()

    if cur_day > phase1:
        return user_target.dci * (1 - user_target.percentage_decrease / 100)
    else:
        if cur_day % 7 == 0:
            number_week = cur_day // 7
        else:
            number_week = cur_day // 7 + 1
        return user_target.dci - 100 * number_week


def get_ideal_DCI(inf):
    """
        inf = (
            info_user.age,
            info_user.height,
            target_user.cur_weight,
            info_user.gender,
            target_user.activity
        )
    """
    if inf[3] == 'woomen':
        DCI = int(
            (655 + (9.6 * inf[2]) + (1.8 * inf[1]) - (4.7 * inf[0])) * ACTIVITY.get(inf[4]))
    else:
        DCI = int(
            (66 + (13.7 * inf[2]) + (5 * inf[1]) - (6.8 * inf[0])) * ACTIVITY.get(inf[4]))
    return DCI


def create_text_stage_4_5(calories, id):
    text = f'Сегодня вы поели на {calories}'
    if SqlMain.get_stage(id) == 5:
        user = User.objects.get(id=id)
        user_program = user.program.last()
        calories_norm = user_program.cur_dci

        calories_last = calories_norm - calories
        if calories / calories_norm * 100 > 100 - K_MESSAGE_DANGER:
            text = f'Сегодня вы поели на {calories}\nОсталось {calories_last}'
            if calories_last < 0:
                text = f'Сегодня вы поели на {calories}\nВы переели на {-calories_last}'
    return text


def create_text_days_eating(calories, id):
    text = f'Сегодня вы поели на {calories}'
    if SqlMain.get_stage(id) == 5:
        user = User.objects.get(id=id)
        user_program = user.program.last()
        calories_norm = user_program.cur_dci

        calories_last = calories_norm - calories
        text = f'Сегодня вы поели на {calories}\nОсталось {calories_last}'
        if calories_last < 0:
            text = f'Сегодня вы поели на {calories}\nВы переели на {-calories_last}'
    return text


def send_yesterday_remind(id, message):
    if SqlMain.get_stage(id) == 5:
        cur_time = datetime.fromtimestamp(message.date)
        user = User.objects.get(id=id)

        day_food = user.day_food.filter(
            time__year=cur_time.year,
            time__month=cur_time.month,
            time__day=cur_time.day
        )

        result_day_dci_all = list(user.result_day_dci.all())

        if len(day_food) == 1:
            if len(result_day_dci_all) >= 2:
                deficit = result_day_dci_all[-2].deficit
                if deficit > 0:
                    mes = Message.objects.filter(
                        mesKey='yesterday_deficit').last().message + f' Вы сэкономили {deficit} калорий'
                else:
                    mes = Message.objects.filter(
                        mesKey='yesterday_proficit').last().message + f' Вы переели  на {-deficit} калорий'
                bot.send_message(
                    chat_id=id,
                    text=mes
                )
