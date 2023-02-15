import telebot
import bot.Button as Button
import bot.InlineKeyboard as InlineKeyboard
from bot.config import TOKEN
from model.models import *


bot = telebot.TeleBot(TOKEN)

# def create_table():
#     cur.executescript('''
#         CREATE TABLE IF NOT EXISTS user
#         (
#             id INTEGER UNIQUE PRIMARY KEY,
#             first_name TEXT,
#             last_name TEXT,
#             username TEXT
#         );

#         CREATE TABLE IF NOT EXISTS food(
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT,
#             calories INTEGER
#         );

#         CREATE TABLE IF NOT EXISTS user_food(    
#             user_id INTEGER NOT NULL,
#             food_id INTEGER NOT NULL,
#             PRIMARY KEY (user_id, food_id),
#             FOREIGN KEY(user_id) REFERENCES user(id),
#             FOREIGN KEY(food_id) REFERENCES food(id)
#         );

#         CREATE TABLE IF NOT EXISTS info_user(
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             age INTEGER DEFAULT 0,
#             height INTEGER DEFAULT 0,
#             gender TEXT DEFAULT "None",
#             ideal_weight FLOAT DEFAULT 0,
#             user INTEGER NOT NULL UNIQUE,
#             FOREIGN KEY(user) REFERENCES user(id)
#         );

#         CREATE TABLE IF NOT EXISTS target_user(
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             type TEXT DEFAULT "None",
#             activity TEXT DEFAULT "None",
#             period INTEGER DEFAULT 0,
#             cur_week INTEGER DEFAULT 0,
#             cur_week_noraml_DCI INTEGER DEFAULT 0,
#             DCI INTEGER DEFAULT 0,
#             cur_DCI INTEGER DEFAULT 0,
#             cur_day_DCI INTEGER DEFAULT 0,
#             cur_weight FLOAT DEFAULT 0,
#             target_weight FLOAT DEFAULT 0,
#             user INTEGER NOT NULL,
#             programm_ready BOOLEAN DEFAULT(FALSE),
#             FOREIGN KEY(user) REFERENCES user(id)
#         );

#         CREATE TABLE IF NOT EXISTS guide(
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             advice TEXT DEFAULT "None",
#             question TEXT DEFAULT "None",
#             answer1 INTEGER DEFAULT 0,
#             answer2 INTEGER DEFAULT 0
#         );

#         CREATE TABLE IF NOT EXISTS user_stage_guide(
#             user INTEGER NOT NULL,
#             stage INTEGER DEFAULT 0,
#             question INTEGER DEFAULT 1,
#             FOREIGN KEY(user) REFERENCES user(id)
#         );
#     ''')
#     con.commit()


def get_user(param):
    if param == 'id':
        id = User.objects.values_list('id', flat=True)
        return list(id)
    elif param == 'username':
        username = User.objects.values_list('username', flat=True)
        return list(username)


# def get_first_last_user_name(message, id, field):
#     if message.from_user.is_bot:
#         id = message.chat.id
#     else:
#         id = message.from_user.id

#     data = (message.text, id)
#     request = f'''UPDATE user SET {field} = ? WHERE id = ?'''
#     cur.execute(request, data)
#     con.commit()
#     cur.execute(
#         '''SELECT * FROM user WHERE id = ?''',
#         (message.from_user.id,)
#     )
#     user = cur.fetchone()
#     bot.delete_message(
#         chat_id=id,
#         message_id=message.message_id
#     )
    
#     bot.edit_message_text(
#         chat_id=id,
#         message_id=message.message_id,
#         text='Вводите необходимые данные',
#         reply_markup=InlineKeyboard.create_InlineKeyboard(user)
#     )


def get_activity(call):
    if call.message.from_user.is_bot:
        id = call.message.chat.id
    else:
        id = call.message.from_user.id

    target_user = TargetUser.objects.get(user=id)
    target_user.activity = call.data
    target_user.save()

    Button.change_DCI_ideal_weight(call.message)
    bot.delete_message(
        chat_id=id,
        message_id=call.message.message_id
    )

    bot.send_message(
        chat_id=id,
        text='Давайте выберем, что вы хотите',
        reply_markup=InlineKeyboard.create_InlineKeyboard_target(
            call.message,
            False
        )
    )

    target_user = TargetUser.objects.get(user=id)
    # проверка переходы на след этап
    if (all([target_user.cur_weight, target_user.target_weight])
        and ('None' not in [target_user.type, target_user.activity])
        and get_stage(id) == 1):

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


def get_gender(call):
    if call.message.from_user.is_bot:
        id = call.message.chat.id
    else:
        id = call.message.from_user.id

    info_user = InfoUser.objects.get(user=id)
    info_user.gender = call.data
    info_user.save()

    Button.change_DCI_ideal_weight(call.message)

    bot.delete_message(
        chat_id=id,
        message_id=call.message.message_id
    )

    bot.send_message(
        chat_id=id,
        text='Укажите следующие данные',
        reply_markup=InlineKeyboard.create_InlineKeyboard_user_info(call.message)
    )

    info_user = InfoUser.objects.get(user=id)
    # проверка переходы на след этап
    if (all([info_user.age, info_user.height])
        and info_user.gender != 'None'
        and get_stage(id) == 0):

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
    for el in foods:
        id_space = el.find(' ')
        if id_space == -1:
            calories = el
            name = None
        else:
            calories = el[:id_space]
            name = el[id_space+1:].strip()

        if not Button.check_int(calories):
            bot.send_message(
                chat_id=id,
                text='Вводите согласно формату, повторите попытку',
                reply_markup=markup
            )
            return
        food, _ = Food.objects.get_or_create(name=name, calories=calories)
        user = User.objects.get(id=id)
        UserFood.objects.get_or_create(
            food=food,
            user=user,
        )
        # try:
        #     name, calories = el.split(' - ')
        #     if not Button.check_int(calories):
        #         bot.send_message(
        #             chat_id=message.chat.id,
        #             text='Вводите согласно формату, повторите попытку',
        #             reply_markup=markup
        #         )
        #         return
        # except:
        #     bot.send_message(
        #         chat_id=message.chat.id,
        #         text='Вводите согласно формату, повторите попытку',
        #         reply_markup=markup
        #     )
        #     return

        # Food.objects.get_or_create(name=name, calories=calories)
        # food = Food.objects.get(name=name, calories=calories)
        # user = User.objects.get(id=id)
        # UserFood.objects.get_or_create(
        #     food=food,
        #     user=user
        # )

    bot.send_message(
        chat_id=id,
        text='Блюдо добавлено'
    )


def get_target(message):
    print('--------------')
    if message.from_user.is_bot:
        id = message.chat.id
    else:
        id = message.from_user.id

    target_user = TargetUser.objects.get(user=id)
    return target_user


def get_info(message):
    if message.from_user.is_bot:
        id = message.chat.id
    else:
        id = message.from_user.id

    info_user = InfoUser.objects.get(user=id)
    return info_user

# def get_programm(message):
#     id = message.chat.id
#     cur.execute(
#         '''SELECT period, cur_week, cur_week_noraml_DCI FROM target_user WHERE user = ?''',
#         (id,)
#     )
#     return cur.fetchone()


# def update_period(id):
#     keyboard = telebot.types.ReplyKeyboardMarkup(True)
#     keyboard.add('Мои данные', 'Моя цель', 'Моя программа', 'Добавить блюдо', 'Что есть в моем рационе', 'Я поел')
#     cur.execute(
#         '''SELECT age, height, gender, ideal_weight
#            FROM info_user
#            WHERE user = ?
#         ''',
#         (id,)
#     )
#     inf = cur.fetchone()
#     if all(inf):
#         cur.execute(
#             '''SELECT DCI, cur_DCI, cur_weight, target_weight, programm_ready
#                FROM target_user
#                WHERE user = ?
#             ''',
#             (id,)
#         )
#         inf = cur.fetchone()
#         if all(inf[:4]):
#             period = int(abs(inf[1] - inf[0]) / 100)
#             cur.execute(
#                 '''UPDATE target_user
#                    SET period = ?
#                    WHERE user = ?
#                 ''',
#                 (period, id)
#             )
#             if inf[4] == False:
#                 cur.execute(
#                     '''UPDATE target_user
#                        SET programm_ready = TRUE
#                        WHERE user = ?
#                     ''',
#                     (id,)
#                 )
#                 bot.send_message(
#                     chat_id=id,
#                     text='Ваша программа готова',
#                     reply_markup=keyboard
#                 )
#             con.commit()
     

def get_stage(id):
    user_stage_guide = UserStageGuide.objects.get(user=id)
    return user_stage_guide.stage


# def get_number_question(id):
#     cur.execute(
#         '''SELECT question FROM user_stage_guide WHERE user = ?''',
#         (id,)
#     )
#     inf = cur.fetchone()
#     return inf[0]


# def get_question(id):
#     cur.execute(
#         '''
#             SELECT guide.advice, guide.question, guide.answer1, guide.answer2
#             FROM guide, user_stage_guide
#             WHERE user_stage_guide.user = ?
#             AND user_stage_guide.question = guide.id
#         ''',
#         (id,)
#     )
#     return cur.fetchone()


# def check_answer(message, questionn):
#     question = questionn[1]
#     answer1 = questionn[2]
#     answer2 = questionn[3]
#     markup = telebot.types.InlineKeyboardMarkup()
#     id = message.from_user.id
#     stage = get_stage(id)

#     if stage == 2:
#         markup.add(telebot.types.InlineKeyboardButton(
#             text='Я все понял, погнали дальше',
#             callback_data='skip_guide'
#         ))
#     else:
#         markup.add(telebot.types.InlineKeyboardButton(
#             text='Я все вспомнил',
#             callback_data='skip_guide'
#         ))
    
#     if not Button.check_int(message.text):
#         bot.send_message(
#             chat_id=id,
#             text=(
#                 f'Вводите целое число, повторите попытку\n'
#                 f'{question}'
#             ),
#             reply_markup=markup
#         )
#         return
#     if int(message.text) < 0:
#         bot.send_message(
#             chat_id=id,
#             text=(
#                 f'Вводите положительное число, повторите попытку\n'
#                 f'{question}'
#             ),
#             reply_markup=markup
#         )
#         return
#     if answer1 <= int(message.text) <= answer2:
#         print('верно')
#         cur.execute(
#             '''
#                 UPDATE user_stage_guide
#                 SET question = question + 1
#                 WHERE user = ?
#             ''',
#             (id,)
#         )
#         con.commit()

#         cur.execute('''SELECT COUNT(*) FROM guide''')
#         count = cur.fetchone()[0]
#         number_question = get_number_question(id)

#         if number_question == count + 1:
#             if stage == 2:
#                 markup = telebot.types.InlineKeyboardMarkup()
#                 markup.add(telebot.types.InlineKeyboardButton(
#                     text='Начать сбор данных',
#                     callback_data='start_get_data'
#                 ))
#                 markup.add(telebot.types.InlineKeyboardButton(
#                     text='Я знаю сколько я ем сейчас',
#                     callback_data='start_get_data'
#                 ))
#                 cur.execute(
#                     '''UPDATE user_stage_guide SET stage = ? WHERE user = ?''',
#                     (3, id)
#                 )
#                 con.commit()

#                 keyboard = InlineKeyboard.create_keyboard_stage(id)
#                 bot.send_message(
#                     chat_id=id,
#                     text='Теперь вы умеете считать калории и определять сколько вы съели в течение дня',
#                     reply_markup=keyboard
#                 )
#                 bot.send_message(
#                     chat_id=id,
#                     text=(
#                         'Настало время определить сколько калорий вы '
#                         'съедаете сейчас. Для этого просто фиксируйте в приложении '
#                         'каждый прием пищи. Если вы уже знаете сколько едите сейчас, '
#                         'то данный шаг можно пропустить.'
#                     ),
#                     reply_markup=markup
#                 )
#                 return
#             bot.send_message(
#                 chat_id=id,
#                 text='Поздравляем, вы вспомнили как считать калории.'
#             )
#             return
#         data = get_question(id)
#         try:
#             bot.send_message(
#                 chat_id=id,
#                 text=data[0]
#             )
#         except:
#             pass
#         bot.send_message(
#             chat_id=id,
#             text=data[1],
#             reply_markup=markup
#         )
#     else:
#         bot.send_message(
#             chat_id=id,
#             text=(
#                 f'Неверно, давайте попробуем еще раз\n'
#                 f'{question}'
#             ),
#             reply_markup=markup
#         )
#         print('неверно')
