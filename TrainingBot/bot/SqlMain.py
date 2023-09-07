import telebot
import bot.Button as Button
import bot.InlineKeyboard as InlineKeyboard
from model.models import *
from TrainingBot.settings import TOKEN
from bot.InlineKeyboard import create_InlineKeyboard_food


bot = telebot.TeleBot(TOKEN)


def get_user(param):
    if param == 'id':
        id = User.objects.values_list('id', flat=True)
        return list(id)
    elif param == 'username':
        username = User.objects.values_list('username', flat=True)
        return list(username)


def get_activity(call):
    if call.message.from_user.is_bot:
        id = call.message.chat.id
    else:
        id = call.message.from_user.id

    target_user = TargetUser.objects.filter(user=id).last()
    target_user.activity = call.data
    target_user.save()

    Button.change_DCI_ideal_weight(call.message)

    markup = InlineKeyboard.create_InlineKeyboard_target(call.message, False)

    # проверка переходы на след этап
    if (all([target_user.cur_weight, target_user.target_weight])
        and ('None' not in [target_user.type, target_user.activity])
            and get_stage(id) == 1):
        if target_user.cur_weight <= target_user.target_weight:
            bot.edit_message_text(
                chat_id=id,
                message_id=call.message.message_id,
                text='Пожалуйста укажите коректный текущий вес и цель',
                reply_markup=markup
            )
            return
        bot.edit_message_text(
            chat_id=id,
            message_id=call.message.message_id,
            text='Укажите следующие данные',
            reply_markup=markup
        )
        Button.update_stage_2(id)
    else:
        bot.edit_message_text(
            chat_id=id,
            message_id=call.message.message_id,
            text='Укажите следующие данные',
            reply_markup=markup
        )


def get_gender(call):
    if call.message.from_user.is_bot:
        id = call.message.chat.id
    else:
        id = call.message.from_user.id

    info_user = InfoUser.objects.get(user=id)
    info_user.gender = call.data
    info_user.save()

    Button.change_DCI_ideal_weight(call.message)

    bot.edit_message_text(
        chat_id=id,
        message_id=call.message.message_id,
        text='Укажите следующие данные',
        reply_markup=InlineKeyboard.create_InlineKeyboard_user_info(
            call.message)
    )

    # проверка переходы на след этап
    if (all([info_user.age, info_user.height])
        and info_user.gender != 'None'
            and get_stage(id) == 0):
        Button.update_stage_1(id)


def get_food(message):
    if message.from_user.is_bot:
        id = message.chat.id
    else:
        id = message.from_user.id

    foods = message.text.split('\n')
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(
        text='Попробовать еще раз',
        callback_data='add_food'
    ))
    markup.add(telebot.types.InlineKeyboardButton(
        text='Закрыть',
        callback_data='close'
    ))
    count_success = 0
    for el in foods:
        id_space = el.find(' ')
        if id_space == -1:
            calories = el
            name = None
        else:
            calories = el[:id_space]
            name = el[id_space+1:].strip()

        if not Button.check_int(calories):
            continue

        count_success += 1
        food, _ = Food.objects.get_or_create(name=name, calories=calories)
        user = User.objects.get(id=id)
        UserFood.objects.get_or_create(
            food=food,
            user=user,
        )

    if not count_success:
        bot.send_message(
            chat_id=id,
            text='Мы не смогли распознать ни одного блюда'
        )
    else:
        bot.send_message(
            chat_id=id,
            text='Блюдо добавлено'
        )
    bot.send_message(
        chat_id=id,
        text='Выберите что вы поели',
        reply_markup=create_InlineKeyboard_food(id)
    )


def get_target(message):
    print('--------------')
    if message.from_user.is_bot:
        id = message.chat.id
    else:
        id = message.from_user.id

    target_user = TargetUser.objects.filter(user=id).last()
    return target_user


def get_info(message):
    if message.from_user.is_bot:
        id = message.chat.id
    else:
        id = message.from_user.id

    info_user = InfoUser.objects.get(user=id)
    return info_user


def get_stage(id):
    user_stage_guide = UserStageGuide.objects.get(user=id)
    return user_stage_guide.stage
