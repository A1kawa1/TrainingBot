import telebot
import bot.InlineKeyboard as InlineKeyboard
import bot.SqlMain as SqlMain
from bot.config import ACTIVITY, TYPE, TOKEN

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

    info_user = InfoUser.objects.get(user=id)
    target_user = TargetUser.objects.get(user=id)
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
            DCI = int((655 + (9.6 * inf[2]) + (1.8 * inf[1]) - (4.7 * inf[0])) * ACTIVITY.get(inf[4]))
        else:
            DCI = int((66 + (13.7 * inf[2]) + (5 * inf[1]) - (6.8 * inf[0])) * ACTIVITY.get(inf[4]))

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

    if field != 'gender' and not check_int(message.text):
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

    target_user = TargetUser.objects.get(user=id)
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

    target_user = TargetUser.objects.get(user=id)

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

    target_user = TargetUser.objects.get(user=id)
    target_user.cur_dci = int(message.text)
    target_user.save()

    if SqlMain.get_stage(id) == 3:
        user_stage_guide = UserStageGuide.objects.get(user=id)
        user_stage_guide.stage = 4
        user_stage_guide.save()

        markup = InlineKeyboard.create_InlineKeyboard_target(message, False)
        bot.send_message(
            chat_id=id,
            text='Вы на 4 этапе',
            reply_markup=InlineKeyboard.create_keyboard_stage(id)
        )
        return
    bot.send_message(
        chat_id=id,
        text='Вы изменили текущий DCI'
    )
    


def change_cur_day_DCI(call, flag=False):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(
        text='Попробовать снова',
        callback_data='own_food'
    ))
    if not flag:
        data = (int(call.data), call.message.chat.id)
    else:
        if not check_int(call.text):
            bot.send_message(
                chat_id=call.from_user.id,
                text='Вводите целое число, повторите попытку',
                reply_markup=markup
            )
            return
        if int(call.text) < 0:
            bot.send_message(
                chat_id=call.from_user.id,
                text='Вводите положительное число, повторите попытку',
                reply_markup=markup
            )
            return
        data = (int(call.text), call.from_user.id)
    target_user = TargetUser.objects.get(user=data[1])
    target_user.cur_day_dci = target_user.cur_day_dci + data[0]
    target_user.save()

    bot.send_message(
        chat_id=data[1],
        text=(f'Вы сегодня поели на {target_user.cur_day_dci} кКл, '
              f'осталось {target_user.cur_week_noraml_dci - target_user.cur_day_dci}')
    )
