from django.core.management.base import BaseCommand
from django.db.models import Avg, Q
from django.core.exceptions import ObjectDoesNotExist
import telebot
from datetime import datetime, time, date
import threading
from time import sleep
from bot.SqlMain import *
from bot.InlineKeyboard import *
from bot.Button import *
from bot.SendMessage import template_send_message, check_remind
from bot.config import ACTIVITY, TYPE, TOKEN


class Command(BaseCommand):
    help = 'Запуск тг бота'

    def handle(self, *args, **options):
        bot = telebot.TeleBot(TOKEN)

        @bot.edited_message_handler(func=lambda _: True)
        def edit(message):
            id = message.from_user.id
            bot.send_message(
                chat_id=id,
                text=f'Вы изменили сообщение на {message.text}'
            )

        @bot.message_handler(commands=['start'])
        def start(message):
            print('start')
            bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
            # print(time_zon := datetime.fromtimestamp(
            #     message.date).astimezone().tzinfo)
            # print(datetime.now(time_zon))
            # print(datetime.now(timezone(timedelta(hours=3))))
            date_start = datetime.fromtimestamp(message.date)
            if message.from_user.is_bot:
                id = message.chat.id
                first_name = message.chat.first_name
                last_name = message.chat.last_name
                username = message.chat.username
            else:
                id = message.from_user.id
                first_name = message.from_user.first_name
                last_name = message.from_user.last_name
                username = message.from_user.username

            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton(
                text='Начать работу',
                callback_data='login'
            ))

            if id in get_user('id'):
                bot.send_message(
                    chat_id=id,
                    text=f'{first_name}, я вижу вы уже пользовались нашими услугами',
                    reply_markup=markup
                )
                return

            user = User(
                id=id,
                first_name=first_name,
                last_name=last_name,
                username=username,
                datetime_start=date_start
            )
            user.save()
            info_user = InfoUser(user=user)
            info_user.save()
            target_user = TargetUser(user=user)
            target_user.save()
            user_stage_guide = UserStageGuide(user=user)
            user_stage_guide.save()
            remind = RemindUser(user=user)
            remind.save()

            template_send_message(bot, id, 'start')
            # bot.send_message(
            #     chat_id=id,
            #     text=(
            #         f'{first_name}, вы новенький. Давайте же я расскажу, что умею.\n'
            #         f'Я помогу следить вам за вашими каллориями. Подберу для вас оптимальную программу питания и тренировок.'
            #     ),
            #     reply_markup=telebot.types.ReplyKeyboardRemove()
            # )
            template_send_message(bot, id, 'start_last')
            # bot.send_message(
            #     chat_id=id,
            #     text='Давайте начнем работу.',
            #     reply_markup=markup
            # )
            user_stage_guide.stage = 0
            user_stage_guide.save()

            # try:
            #     cur.execute(
            #         '''SELECT username, first_name FROM user WHERE id = ?''',
            #         (id,)
            #     )
            #     inf = cur.fetchall()
            #     if len(inf) != 0:
            #         if (id,) in get_user('id') and inf[0][0] is None:
            #             print(None)
            #             cur.execute(
            #                 '''DELETE FROM user WHERE id = ?''',
            #                 (id,)
            #             )
            #             cur.execute(
            #                 '''DELETE FROM info_user WHERE user = ?''',
            #                 (id,)
            #             )
            #             cur.execute(
            #                 '''DELETE FROM target_user WHERE user = ?''',
            #                 (id,)
            #             )
            #             con.commit()
            #     cur.execute(
            #         '''INSERT INTO user VALUES(?, ?, ?, ?);''',
            #         data_user
            #     )
            #     cur.execute(
            #         '''INSERT INTO info_user VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?);''',
            #         data_info
            #     )
            #     cur.execute(
            #         '''INSERT INTO target_user VALUES(?, ?, ?, ?, ?, ?, ?, ?);''',
            #         data_target
            #     )
            #     con.commit()
            #     bot.delete_message(
            #         chat_id=id,
            #         message_id=message.message_id,
            #     )
            #     markup.add(telebot.types.InlineKeyboardButton(
            #         text='Начать работу',
            #         callback_data='login'
            #     ))
            #     bot.send_message(
            #         chat_id=id,
            #         text=f'{first_name}, вы успешно зарегистрировались',
            #         reply_markup=markup
            #     )

            # except Exception as e:
            #     print(e)
            #     cur.execute(
            #         '''SELECT username, first_name FROM user WHERE id = ?''',
            #         (id,)
            #     )
            #     inf = cur.fetchall()
            #     username = inf[0][0]
            #     name = inf[0][1]
            #     markup.add(telebot.types.InlineKeyboardButton(
            #         text='Начать работу',
            #         callback_data='login'
            #     ))
            #     bot.send_message(
            #         chat_id=id,
            #         text=f'{name}, вы уже зарегистрированны',
            #         reply_markup=markup
            #     )

        # def check_on_guide(message):
        #     id = message.from_user.id
        #     if (id,) not in get_user('id'):
        #         return False
        #     stage = get_stage(id)
        #     if stage == 2 or message.text == 'Мастер обучения':
        #         return True
        #     return False

        # @bot.message_handler(func=check_on_guide)
        # def guide(message):
        #     # это будет работать, если Мастер обучения всегда возвращает в начало
        #     id = message.from_user.id
        #     if message.text == 'Мастер обучения':
        #         bot.clear_step_handler_by_chat_id(chat_id=id)
        #         print('guide_again_start')
        #         cur.execute(
        #             '''
        #                 UPDATE user_stage_guide
        #                 SET question = 1
        #                 WHERE user = ?
        #             ''',
        #             (id,)
        #         )
        #         con.commit()

        #         markup = telebot.types.InlineKeyboardMarkup()
        #         data = get_question(id)
        #         markup.add(telebot.types.InlineKeyboardButton(
        #             text='Я все вспомнил',
        #             callback_data='skip_guide'
        #         ))
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
        #         question = get_question(id)
        #         print(question)
        #         check_answer(message, question)

            # это отлично работает
            # id = message.from_user.id
            # number_question = get_number_question(id)

            # cur.execute('''SELECT COUNT(*) FROM guide''')
            # count = cur.fetchone()[0]
            # if get_stage(id) == 2:
            #     question = get_question(id)
            #     print(question)
            #     check_answer(message, question)
            # else:
            #     if number_question == count + 1:
            #         bot.clear_step_handler_by_chat_id(chat_id=id)
            #         print('guide_again_start')
            #         cur.execute(
            #             '''
            #                 UPDATE user_stage_guide
            #                 SET question = 1
            #                 WHERE user = ?
            #             ''',
            #             (id,)
            #         )
            #         con.commit()

            #         markup = telebot.types.InlineKeyboardMarkup()
            #         data = get_question(id)
            #         markup.add(telebot.types.InlineKeyboardButton(
            #             text='Я все вспомнил',
            #             callback_data='skip_guide'
            #         ))
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
            #         print('guide_again')
            #         question = get_question(id)
            #         print(question)
            #         check_answer(message, question)

        def stage_4_5_calories(message):
            id = message.from_user.id
            if id not in get_user('id'):
                return False

            if get_stage(id) in (4, 5):
                if any([x in message.text for x in ['-', '!', '^', ',', ';', ':', '#', '%', '?', r'\n']]):
                    bot.send_message(
                        chat_id=id,
                        text='Вводите согласно формату, повторите попытку',
                    )
                    return False
                tmp = message.text.split('+')
                if len(tmp) == 1:
                    id_space = message.text.find(' ')

                    try:
                        if id_space == -1:
                            calories = int(message.text)
                        else:
                            calories = message.text[:id_space]

                        if check_int(calories):
                            return True
                    except:
                        if message.text not in (
                            'Мастер обучения', 'Меню',
                            'Статистика за день', 'Мониторинг',
                                'Мои данные', 'Моя цель', 'Сброс'):
                            bot.send_message(
                                chat_id=id,
                                text='Вводите согласно формату, повторите попытку',
                            )
                        return False
                if check_int(tmp[0]):
                    return True
            return False

        @bot.message_handler(func=stage_4_5_calories)
        def calories(message):
            tmp = message.text.split('+')
            if len(tmp) == 1:
                id_space = message.text.find(' ')
                if id_space == -1:
                    calories = int(message.text)
                    name = None
                else:
                    calories = message.text[:id_space]
                    name = message.text[id_space+1:].strip()
                if not Button.check_int(calories):
                    bot.send_message(
                        chat_id=id,
                        text='Вводите согласно формату, повторите попытку',
                    )
                    return
                data = (int(calories), message.from_user.id)
            else:
                name = None
                tmp = list(map(lambda x: x.strip(), tmp))
                id_space = tmp[-1].find(' ')

                if id_space == -1:
                    calories = tmp[:-1] + [tmp[-1]]
                    name = None
                else:
                    calories = tmp[:-1] + [tmp[-1][:id_space]]
                    name = tmp[-1][id_space+1:].strip()

                try:
                    data = (sum(list(map(int, calories))),
                            message.from_user.id)
                except ValueError:
                    bot.send_message(
                        chat_id=data[1],
                        text=f'Простите, но мы не смогли распознать ваши данные'
                    )

            food_user = UserDayFood(
                user=User.objects.get(id=data[1]),
                calories=data[0],
                name=name,
                time=datetime.fromtimestamp(message.date)
            )
            food_user.save()

            calories = update_result_day_DCI(message)
            if calories == 'dci_success':
                update_stage_5(data[1], message)
                return

            text = create_text_stage_4_5(calories, data[1])
            # text = f'Сегодня вы поели на {calories}'
            # if SqlMain.get_stage(data[1]) == 5:
            #     calories_norm = UserProgram.objects.filter(
            #         user=data[1]).last().cur_dci
            #     print(calories / calories_norm * 100)
            #     if calories / calories_norm * 100 > 100 - K_MESSAGE_DANGER:
            #         text = f'Сегодня вы поели на {calories}\nОсталось {calories_norm-calories}'
            #         if calories > calories_norm:
            #             text = f'Сегодня вы поели на {calories}\nВы переели на {-(calories_norm-calories)}'
            bot.send_message(
                chat_id=data[1],
                text=text
            )
            send_yesterday_remind(data[1], message)

        @bot.message_handler(content_types='text')
        def info(message):
            try:
                bot.clear_step_handler_by_chat_id(chat_id=message.from_user.id)
                id = message.from_user.id

                if id not in get_user('id'):
                    print('not user')
                    start(message)
                # elif message.text == 'Добавить блюдо':
                #     markup = telebot.types.InlineKeyboardMarkup()
                #     markup.add(telebot.types.InlineKeyboardButton(
                #         text='Закрыть',
                #         callback_data='close'
                #     ))
                #     bot.send_message(
                #         chat_id=id,
                #         text='Отправьте название и каллорийность\nв виде: кКл блюдо\n(несколько блюд вводите с новой строки)',
                #         reply_markup=markup
                #     )
                #     bot.register_next_step_handler(message, get_food)
                elif message.text == 'Сброс':
                    markup = telebot.types.InlineKeyboardMarkup()
                    markup.add(telebot.types.InlineKeyboardButton(
                        text='Подтвердить',
                        callback_data='delete_profile'
                    ))
                    markup.add(telebot.types.InlineKeyboardButton(
                        text='Закрыть',
                        callback_data='close'
                    ))
                    bot.send_message(
                        chat_id=id,
                        text='Подтвердите сброс аккаунта',
                        reply_markup=markup
                    )
                elif message.text == 'Что есть в моем рационе':

                    user = User.objects.get(id=id)
                    foods = UserFood.objects.filter(user=user)

                    if not foods.exists():
                        bot.send_message(
                            chat_id=id,
                            text='Ничего'
                        )
                        return
                    text = ''
                    for food in foods:
                        text += f'{food.food.name} - {food.food.calories}\n'
                    bot.send_message(
                        chat_id=id,
                        text=text
                    )
                elif message.text == 'Мои данные':
                    bot.send_message(
                        chat_id=id,
                        text='Укажите следующие данные',
                        reply_markup=create_InlineKeyboard_user_info(message)
                    )
                elif message.text == 'Меню':
                    bot.send_message(
                        chat_id=id,
                        text='Выберите что вы поели',
                        reply_markup=create_InlineKeyboard_food(id)
                    )
                elif message.text == 'Моя цель':
                    bot.send_message(
                        chat_id=id,
                        text='Давайте выберем, что вы хотите',
                        reply_markup=create_InlineKeyboard_target(
                            message, False)
                    )
                elif message.text == 'Я все вспомнил':
                    bot.send_message(
                        chat_id=id,
                        text='Поздравляем, вы вспомнили как считать калории.',
                        reply_markup=create_keyboard_stage(id)
                    )
                elif message.text == 'Завершить обучение':
                    update_stage_3(id)
                elif message.text == 'Мастер обучения':
                    markup = telebot.types.InlineKeyboardMarkup()
                    keyboard = telebot.types.ReplyKeyboardMarkup(True)
                    keyboard.add('Я все вспомнил')

                    markup.add(telebot.types.InlineKeyboardButton(
                        text='Пройти курс',
                        url=f'http://127.0.0.1:8000/{id}/'
                    ))
                    markup.add(telebot.types.InlineKeyboardButton(
                        text='Я все вспомнил',
                        callback_data='skip_guide'
                    ))

                    bot.send_message(
                        chat_id=id,
                        text='Давайте же вспомним как считать калории.',
                        reply_markup=keyboard
                    )
                    bot.send_message(
                        chat_id=id,
                        text='Для этого пожалуйста перейдите по ссылке и ответьте на несколько простых вопросов.',
                        reply_markup=markup
                    )
                elif message.text == 'Я знаю сколько я ем сейчас':
                    markup = telebot.types.InlineKeyboardMarkup()
                    markup.add(telebot.types.InlineKeyboardButton(
                        text='Закрыть',
                        callback_data='close'
                    ))
                    bot.send_message(
                        chat_id=id,
                        text=(
                            'Укажите сколько калорий вы съедаете сейчас в сутки и '
                            'мы рассчитаем программу управления весом для '
                            'достижения достигнутой цели.'
                        ),
                        reply_markup=markup
                    )
                    bot.register_next_step_handler(message, change_cur_DCI)
                elif message.text == 'Начать сбор данных':
                    update_stage_4(id)
                elif message.text == 'Статистика за день':

                    # user = User.objects.get(id=id)
                    # cur_time = datetime.fromtimestamp(message.date)

                    # calories = user.day_food.filter(
                    #     time__year=cur_time.year,
                    #     time__month=cur_time.month,
                    #     time__day=cur_time.day
                    # ).aggregate(Sum('calories')).get('calories__sum')

                    calories = update_result_day_DCI(message)
                    if calories == 'dci_success':
                        update_stage_5(id, message)
                        return

                    text = create_text_days_eating(calories, id)

                    bot.send_message(
                        chat_id=id,
                        text=text,
                        reply_markup=cur_day_food(id, message.date)
                    )
                elif message.text == 'Статистика за неделю':
                    bot.send_message(
                        chat_id=id,
                        text='Приемы пищи за последние 7 дней',
                        reply_markup=create_inline_week_eating(id, message)
                    )
                elif message.text == 'Мониторинг':
                    count_day = ResultDayDci.objects.filter(user=id).count()
                    data = ResultDayDci.objects.filter(
                        user=id).order_by('date')
                    if count_day == 0:
                        avg_dci = 0
                    elif count_day == 1:
                        avg_dci = data[0].calories
                    elif count_day in (2, 3):
                        avg_dci = data[1].calories
                    else:
                        avg_dci = int(
                            (ResultDayDci.objects.filter(user=id)
                             .order_by('date')[1:len(data)-1]
                             .aggregate(Avg('calories'))
                             .get('calories__avg'))
                        )

                    markup = telebot.types.InlineKeyboardMarkup()
                    markup.add(telebot.types.InlineKeyboardButton(
                        text=f'Дней мониторинга: {count_day}',
                        callback_data='asdasdf'
                    ))
                    markup.add(telebot.types.InlineKeyboardButton(
                        text=f'Регулярность ввода данных: {int(count_day / 4 * 100) if count_day <= 4 else 100}%',
                        callback_data='asdasdf'
                    ))
                    markup.add(telebot.types.InlineKeyboardButton(
                        text=f'Текущее кол-во калорий в день: {avg_dci}',
                        callback_data='asdasdf'
                    ))
                    bot.send_message(
                        chat_id=id,
                        text='Мы еще не уверены сколько вы едите в день.\nТекущие показатели мониторинга следующие:',
                        reply_markup=markup
                    )
                    markup = telebot.types.InlineKeyboardMarkup()
                    markup.add(telebot.types.InlineKeyboardButton(
                        text='Завершить мониторинг',
                        callback_data='end_monitoring'
                    ))
                    markup.add(telebot.types.InlineKeyboardButton(
                        text='Продолжить мониторинг',
                        callback_data='continue_monitoring'
                    ))
                    bot.send_message(
                        chat_id=id,
                        text='Если вы хотите завершить мониторинг, то придется ввести текущее кол-во калорий вручную.',
                        reply_markup=markup
                    )
                elif message.text == 'Моя программа':
                    cur_time = datetime.fromtimestamp(message.date)
                    cur_date = date(
                        cur_time.year, cur_time.month, cur_time.day)
                    user = User.objects.get(id=id)
                    user_program = user.program.last()
                    # if len(user.result_day_dci.filter(date=cur_date)) == 0 and user_program.date_start != cur_date:
                    #     user_program.cur_day += 1
                    #     user_program.save()
                    if len(user.result_day_dci.filter(date=cur_date)) == 0 and user_program.date_start != cur_date:
                        user_program.cur_day = (
                            cur_date - user_program.date_start).days + 1
                        user_program.save()
                    # if not ResultDayDci.objects.filter(
                    #     user=user,
                    #     date=cur_date
                    # ).exists():
                    #     result_dci = ResultDayDci(
                    #         user=user,
                    #         date=cur_date
                    #     )
                    #     result_dci.save()
                    day_result, create = ResultDayDci.objects.get_or_create(
                        user=user,
                        date=cur_date
                    )
                    if create == True:
                        day_result.deficit = user_program.cur_dci
                    day_result.save()
                    bot.send_message(
                        chat_id=id,
                        text=('Ваша программа'),
                        reply_markup=create_inline_program(id)
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

        @bot.callback_query_handler(func=lambda call: True)
        def query_handler(call):
            markup = telebot.types.InlineKeyboardMarkup()
            # elif call.data == 'not_get_info_tg':
            #     try:
            #         id = call.message.chat.id
            #         cur.execute(
            #             '''SELECT username, first_name, last_name FROM user WHERE id = ?''',
            #             (id,)
            #         )
            #         inf = cur.fetchall()
            #         first_name, last_name = None, None
            #         if len(inf) != 0:
            #             if (id,) in get_user('id') and inf[0][0] is None:
            #                 print(None)
            #                 first_name = inf[0][1]
            #                 last_name = inf[0][2]
            #                 print(first_name, last_name)
            #                 cur.execute(
            #                     '''DELETE FROM user WHERE id = ?''',
            #                     (id,)
            #                 )
            #                 cur.execute(
            #                     '''DELETE FROM info_user WHERE user = ?''',
            #                     (id,)
            #                 )
            #                 cur.execute(
            #                     '''DELETE FROM target_user WHERE user = ?''',
            #                     (id,)
            #                 )
            #                 con.commit()
            #         data_user = (id, first_name, last_name, None)
            #         data_info = (None, 0, 0, 0, 'None', 0, 0, 'отсутствует или минимальная', 0, id)
            #         data_target = (None, None, 0, 0, id)
            #         cur.execute(
            #             '''INSERT INTO user VALUES(?, ?, ?, ?);''',
            #             data_user
            #         )
            #         cur.execute(
            #             '''INSERT INTO info_user VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?);''',
            #             data_info
            #         )
            #         cur.execute(
            #             '''INSERT INTO target_user VALUES(?, ?, ?, ?, ?);''',
            #             data_target
            #         )
            #         con.commit()

            #         cur.execute(
            #             '''SELECT * FROM user WHERE id = ?''',
            #             (id,)
            #         )
            #         user = cur.fetchall()[0]
            #         markup = create_InlineKeyboard(user)
            #         bot.delete_message(
            #             chat_id=call.message.chat.id,
            #             message_id=call.message.message_id,
            #         )
            #         bot.send_message(
            #             chat_id=call.message.chat.id,
            #             text='Давайте начнем регистрацию',
            #             reply_markup=telebot.types.ReplyKeyboardRemove()
            #         )
            #         bot.send_message(
            #             chat_id=call.message.chat.id,
            #             text='Вводите необходимые данные',
            #             reply_markup=markup
            #         )
            #     except Exception as e:
            #         print(e)
            #         cur.execute(
            #             '''SELECT username, first_name FROM user WHERE id = ?''',
            #             (id,)
            #         )
            #         inf = cur.fetchall()
            #         print(inf)
            #         username = inf[0][0]
            #         name = inf[0][1]
            #         markup.add(telebot.types.InlineKeyboardButton(
            #             text='Войти',
            #             callback_data='login'
            #         ))
            #         bot.send_message(
            #             chat_id=call.message.chat.id,
            #             text=f'{name}, вы уже зарегистрированны\nваш ник - {username}',
            #             reply_markup=markup
            #         )
            try:
                id = call.message.chat.id
                if call.data == 'close':
                    bot.delete_message(
                        chat_id=id,
                        message_id=call.message.message_id
                    )
                    bot.clear_step_handler_by_chat_id(chat_id=id)
                elif id not in get_user('id'):
                    start(call.message)
                elif call.data == 'delete_profile':
                    user = User.objects.get(id=id)
                    user.delete()
                    start(call.message)
                elif call.data == 'login':
                    if get_stage(id) != 0:
                        bot.send_message(
                            chat_id=id,
                            text='Давайте же продолжим работу',
                            reply_markup=create_keyboard_stage(id)
                        )
                        return
                    template_send_message(bot, id, 'stage0')
                    # bot.send_message(
                    #     chat_id=id,
                    #     text=('Мы рады, что вы присоединились к нам. '
                    #           'Укажите дополнительные данные, '
                    #           'мы будем использовать в дальнейшем для построения программы управления весом.'),
                    #     reply_markup=create_keyboard_stage(id)
                    # )
                    bot.send_message(
                        chat_id=id,
                        text='Укажите следующие данные',
                        reply_markup=create_InlineKeyboard_user_info(
                            call.message)
                    )
                # elif call.data in ['first_name', 'last_name', 'username']:
                #     cur.execute(
                #         '''SELECT * FROM user WHERE id = ?''',
                #         (id,)
                #     )
                #     user = cur.fetchone()
                #     markup = create_InlineKeyboard(user)
                #     TEXT_FUNC = {
                #         'first_name': ['Имя', 'first_name'],
                #         'last_name': ['Фамилию', 'last_name'],
                #         'username': ['Никнейм', 'username'],
                #     }
                #     text = f'Введиите {TEXT_FUNC[call.data][0]}'
                #     bot.edit_message_text(
                #         chat_id=id,
                #         message_id=call.message.message_id,
                #         text=text,
                #         reply_markup=markup
                #     )
                #     bot.register_next_step_handler(call.message, get_first_last_user_name, call.message.message_id, TEXT_FUNC[call.data][1])
                elif call.data in ['change_height', 'change_age']:
                    markup.add(telebot.types.InlineKeyboardButton(
                        text='Закрыть',
                        callback_data='close'
                    ))
                    bot.delete_message(
                        chat_id=id,
                        message_id=call.message.message_id
                    )
                    TEXT_FUNC = {
                        'change_age': ['возраст', 'age'],
                        'change_height': ['рост (см)', 'height'],
                    }
                    text = f'Укажите свой {TEXT_FUNC[call.data][0]}'
                    bot.send_message(
                        chat_id=id,
                        text=text,
                        reply_markup=markup
                    )
                    bot.register_next_step_handler(
                        call.message, change_info, TEXT_FUNC[call.data][1])
                elif call.data in ['change_target', 'change_weight']:
                    markup.add(telebot.types.InlineKeyboardButton(
                        text='Закрыть',
                        callback_data='close'
                    ))
                    bot.delete_message(
                        chat_id=id,
                        message_id=call.message.message_id
                    )
                    TEXT_FUNC = {
                        'change_target': ['новую цель (кг)', 'target_weight'],
                        'change_weight': ['текущий вес (кг)', 'cur_weight']
                    }
                    text = f'Укажите {TEXT_FUNC[call.data][0]}'
                    bot.send_message(
                        chat_id=id,
                        text=text,
                        reply_markup=markup
                    )
                    bot.register_next_step_handler(
                        call.message, change_target_weight, TEXT_FUNC[call.data][1])
                # elif call.data == 'change_cur_DCI':
                #     markup.add(telebot.types.InlineKeyboardButton(
                #         text='Закрыть',
                #         callback_data='close'
                #     ))
                #     bot.delete_message(
                #         chat_id=id,
                #         message_id=call.message.message_id
                #     )
                #     bot.send_message(
                #         chat_id=id,
                #         text='Укажите текущий DCI (кКл)',
                #         reply_markup=markup
                #     )
                #     bot.register_next_step_handler(call.message, change_cur_DCI)
                elif call.data == 'change_gender':
                    bot.delete_message(
                        chat_id=id,
                        message_id=call.message.message_id
                    )

                    markup.add(telebot.types.InlineKeyboardButton(
                        text='М',
                        callback_data='men'
                    ))
                    markup.add(telebot.types.InlineKeyboardButton(
                        text='Ж',
                        callback_data='woomen'
                    ))
                    markup.add(telebot.types.InlineKeyboardButton(
                        text='Закрыть',
                        callback_data='close'
                    ))
                    bot.send_message(
                        chat_id=id,
                        text='Укажите свой пол',
                        reply_markup=markup
                    )
                elif call.data in ['men', 'woomen']:
                    get_gender(call)
                elif call.data == 'change_activity':
                    bot.delete_message(
                        chat_id=id,
                        message_id=call.message.message_id
                    )
                    for el in list(ACTIVITY.keys())[:-1]:
                        markup.add(telebot.types.InlineKeyboardButton(
                            text=el,
                            callback_data=el
                        ))
                    markup.add(telebot.types.InlineKeyboardButton(
                        text='Закрыть',
                        callback_data='close'
                    ))
                    bot.send_message(
                        chat_id=id,
                        text='Выберите новую активность',
                        reply_markup=markup
                    )
                elif call.data in ACTIVITY.keys():
                    get_activity(call)
                elif call.data == 'add_food':
                    markup.add(telebot.types.InlineKeyboardButton(
                        text='Закрыть',
                        callback_data='close'
                    ))
                    bot.send_message(
                        chat_id=id,
                        text='Отправьте название и каллорийность\nв виде: кКл блюдо\n(несколько блюд вводите с новой строки)',
                        reply_markup=markup
                    )
                    bot.register_next_step_handler(call.message, get_food)
                elif call.data.startswith('food_'):
                    add_from_menu_day_DCI(call)
                # elif call.data == 'own_food':
                #     markup.add(telebot.types.InlineKeyboardButton(
                #         text='Закрыть',
                #         callback_data='close'
                #     ))
                #     bot.delete_message(
                #         chat_id=id,
                #         message_id=call.message.message_id
                #     )
                #     bot.send_message(
                #         chat_id=id,
                #         text='Введите кол-во кКл, которое вы съели',
                #         reply_markup=markup
                #     )
                #     bot.register_next_step_handler(call.message, change_cur_day_DCI, True)
                elif call.data.startswith('detail_'):
                    _, food_id = call.data.split('_')
                    bot.delete_message(
                        chat_id=id,
                        message_id=call.message.message_id
                    )
                    detail_food(food_id, id)
                elif call.data.startswith('delete_day_dci_'):
                    food_id = call.data[15:]
                    bot.delete_message(
                        chat_id=id,
                        message_id=call.message.message_id
                    )

                    delete_day_DCI(call.message, food_id)

                elif call.data.startswith('change_day_dci_'):
                    markup.add(telebot.types.InlineKeyboardButton(
                        text='Закрыть',
                        callback_data='close'
                    ))
                    bot.delete_message(
                        chat_id=id,
                        message_id=call.message.message_id
                    )
                    bot.send_message(
                        chat_id=id,
                        text='Введите новые данные\nв виде - кКл блюдо',
                        reply_markup=markup
                    )
                    food_id = call.data[15:]
                    bot.register_next_step_handler(
                        call.message, change_day_DCI, food_id)
                elif call.data in TYPE:
                    target_user = TargetUser.objects.filter(user=id).last()
                    target_user.type = call.data
                    target_user.save()

                    bot.edit_message_text(
                        chat_id=id,
                        message_id=call.message.message_id,
                        text='Укажите следующие данные',
                        reply_markup=create_InlineKeyboard_target(
                            call.message, False)
                    )
                elif call.data == 'my_target':
                    bot.edit_message_text(
                        chat_id=id,
                        message_id=call.message.message_id,
                        text='Давайте выберем, что вы хотите',
                        reply_markup=create_InlineKeyboard_target(
                            call.message, True)
                    )
                elif call.data == 'my_info':
                    bot.edit_message_text(
                        chat_id=id,
                        message_id=call.message.message_id,
                        text='Укажите следующие данные',
                        reply_markup=create_InlineKeyboard_user_info(
                            call.message)
                    )
                elif call.data == 'create_target':
                    bot.send_message(
                        chat_id=id,
                        text='Давайте выберем, что вы хотите',
                        reply_markup=create_InlineKeyboard_target(
                            call.message, False)
                    )
                elif call.data == 'start_guide':
                    id = id
                    keyboard = telebot.types.ReplyKeyboardMarkup(True)
                    keyboard.add('Завершить обучение')
                    markup.add(telebot.types.InlineKeyboardButton(
                        text='Пройти курс',
                        url=f'http://127.0.0.1:8000/{id}/'
                    ))
                    markup.add(telebot.types.InlineKeyboardButton(
                        text='Завершить обучение',
                        callback_data='skip_guide'
                    ))
                    bot.send_message(
                        chat_id=id,
                        text='Давайте же начнем обучение.',
                        reply_markup=keyboard
                    )
                    bot.send_message(
                        chat_id=id,
                        text='Для его прохождение пожалуйста перейдите по ссылке и ответьте на несколько простых вопросов.',
                        reply_markup=markup
                    )
                    # # попытка первая
                    # data = get_question(id)
                    # markup.add(telebot.types.InlineKeyboardButton(
                    #     text='Я все понял, погнали дальше',
                    #     callback_data='skip_guide'
                    # ))
                    # try:
                    #     bot.send_message(
                    #         chat_id=id,
                    #         text=data[0]
                    #     )
                    # except:
                    #     pass
                    # bot.send_message(
                    #     chat_id=id,
                    #     text=data[1],
                    #     reply_markup=markup
                    # )
                    # print('end')
                elif call.data == 'skip_guide':
                    bot.clear_step_handler_by_chat_id(chat_id=id)

                    if get_stage(id) > 2:
                        bot.send_message(
                            chat_id=id,
                            text='Поздравляем, вы вспомнили как считать калории.',
                            reply_markup=create_keyboard_stage(id)
                        )
                        return

                    update_stage_3(id)
                elif call.data in ['get_cur_DCI', 'end_monitoring']:
                    markup.add(telebot.types.InlineKeyboardButton(
                        text='Закрыть',
                        callback_data='close'
                    ))
                    bot.send_message(
                        chat_id=id,
                        text=(
                            'Укажите сколько калорий вы съедаете сейчас в сутки и '
                            'мы рассчитаем программу управления весом для '
                            'достижения достигнутой цели.'
                        ),
                        reply_markup=markup
                    )
                    bot.register_next_step_handler(
                        call.message, change_cur_DCI)
                elif call.data == 'start_get_cur_DCI':
                    update_stage_4(id)
                elif call.data == 'continue_monitoring':
                    bot.send_message(
                        chat_id=id,
                        text='Тогда давайте продолжим'
                    )
                elif call.data == 'program':
                    bot.send_message(
                        chat_id=id,
                        text=('Ваша программа'),
                        reply_markup=create_inline_program(id)
                    )
                elif call.data == 'change_weight_in_program':
                    markup.add(telebot.types.InlineKeyboardButton(
                        text='Закрыть',
                        callback_data='close'
                    ))
                    bot.delete_message(
                        chat_id=id,
                        message_id=call.message.message_id
                    )
                    bot.send_message(
                        chat_id=id,
                        text='Укажите ваш текущий вес',
                        reply_markup=markup
                    )
                    bot.register_next_step_handler(
                        call.message, change_weight_in_program)
                elif call.data == 'week_eating':
                    bot.send_message(
                        chat_id=id,
                        text='Приемы пищи за последние 7 дней',
                        reply_markup=create_inline_week_eating(
                            id, call.message)
                    )
                elif call.data.startswith('edit_week_eating_'):
                    eating_id = int(call.data[17:])
                    date = ResultDayDci.objects.get(id=eating_id).date
                    markup.add(telebot.types.InlineKeyboardButton(
                        text='Закрыть',
                        callback_data='close'
                    ))
                    bot.delete_message(
                        chat_id=id,
                        message_id=call.message.message_id
                    )
                    bot.send_message(
                        chat_id=id,
                        text=f'{date.strftime("%d:%m:%Y")}\nВведите новое количество калорий',
                        reply_markup=markup
                    )
                    bot.register_next_step_handler(
                        call.message, week_eating, eating_id)
                elif call.data == 'change_cur_target':
                    markup.add(telebot.types.InlineKeyboardButton(
                        text='Подтверждаю изменение текущей цели',
                        callback_data='confirm_change_cur_target'
                    ))
                    markup.add(telebot.types.InlineKeyboardButton(
                        text='Закрыть',
                        callback_data='close'
                    ))
                    bot.send_message(
                        chat_id=id,
                        text='При изменении цели необходимо будетт указать '
                        'новый желаемый вес. При этом программа похудения '
                        'будет перестроена и отсчет программы начнется заново.',
                        reply_markup=markup
                    )
                elif call.data == 'confirm_change_cur_target':
                    markup.add(telebot.types.InlineKeyboardButton(
                        text='Закрыть',
                        callback_data='close'
                    ))
                    bot.send_message(
                        chat_id=id,
                        text='Сколько вы хотите весить',
                        reply_markup=markup
                    )
                    bot.register_next_step_handler(
                        call.message, change_cur_target)
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

        # def test():
        #     while True:
        #         print(User.objects.all())
        #         sleep(3)
        # def schedule_checker():
        #     while True:
        #         schedule.run_pending()
        #         sleep(5)

        # def refresh_info_user():
        #     cur.execute('''
        #         UPDATE info_user SET period = period - 1 WHERE period > 0;
        #     ''')
        #     con.commit()

        # def update_period():
        #     while True:
        #         try:
        #             cur.execute(
        #                 '''SELECT age, height, gender, ideal_weight, user
        #                 FROM info_user
        #                 '''
        #             )
        #             users = cur.fetchall()
        #             if len(users) != 0:
        #                 for user in users:
        #                     if (user[0] != 0 and user[1] != 0
        #                         and user[2] != 'None' and user[3] != 0):
        #                         cur.execute(
        #                             '''SELECT DCI, cur_DCI, programm_ready FROM target_user WHERE user = ?''',
        #                             (user[4],)
        #                         )
        #                         inf = cur.fetchall()[0]

        #         except:
        #             pass

        # schedule.every().day.at('00:00').do(refresh_info_user)
        # Thread(target=schedule_checker).start()
        # Thread(target=update_period).start()
        # Thread(target=test).start()

            # print(time_zon := datetime.fromtimestamp(
            #     message.date).astimezone().tzinfo)
            # print(datetime.now(time_zon))
            # print(datetime.now(timezone(timedelta(hours=3))))

        def bg_thread():
            while True:
                cur_time = datetime.now().date()
                reminds = UserStageGuide.objects.select_related(
                    'user').filter(Q(stage__in=[4, 5])
                                   & (Q(user__remind__remind_first=True)
                                      | Q(user__remind__remind_second=True)
                                      | (Q(user__remind__day_without_indication_weight=0)
                                         & Q(user__remind__remind_weight=True))))
                set_flags = UserStageGuide.objects.select_related(
                    'user').filter(Q(stage__in=[4, 5])
                                   & (Q(user__remind__remind_first=False)
                                      & Q(user__remind__remind_second=False)))
                for remind in reminds:
                    try:
                        user = remind.user
                        remind = user.remind.last()
                        time_zon = user.datetime_start.astimezone().tzinfo
                        cur_time = datetime.now(time_zon)
                        res = check_remind(cur_time, user)

                        if res == 'send_weight':
                            template_send_message(
                                bot, user.id, 'remind_weight')
                            remind.day_without_indication_weight = 1
                            remind.remind_weight = False
                            remind.save()
                        elif res == 'send_first':
                            template_send_message(
                                bot, user.id, 'remind_first')
                            remind.remind_first = False
                            remind.save()
                            cur_date = cur_time.date()
                            day_result, create = ResultDayDci.objects.get_or_create(
                                user=user,
                                date=cur_date
                            )
                            if create == True:
                                target_user = user.target.last()
                                program_user = target_user.program
                                day_result.deficit = program_user.cur_dci
                                if program_user.date_start != cur_date:
                                    program_user.cur_day = (
                                        cur_date - program_user.date_start).days + 1
                                    program_user.save()
                                day_result.save()
                        elif res == 'send_second':
                            template_send_message(
                                bot, user.id, 'remind_second')
                            remind.remind_second = False
                            remind.save()
                        if (cur_time.time() < time(hour=9, minute=0, second=0)
                                and (remind.remind_second == False or remind.remind_first == False or remind.remind_weight == False)):
                            remind.remind_first = True
                            remind.remind_second = True
                            remind.remind_weight = True
                            if remind.day_without_indication_weight == 0:
                                remind.day_without_indication_weight = 1
                            remind.save()
                    except Exception:
                        ...
                for set_flag in set_flags:
                    user = set_flag.user
                    remind = user.remind.last()
                    time_zon = user.datetime_start.astimezone().tzinfo
                    cur_time = datetime.now(time_zon)
                    if cur_time.time() < time(hour=9, minute=0, second=0):
                        remind.remind_first = True
                        remind.remind_second = True
                        remind.remind_weight = True
                        if remind.day_without_indication_weight == 0:
                            remind.day_without_indication_weight = 1
                        remind.save()
                sleep(5)
                # users_id = list(UserStageGuide.objects.filter(
                #     stage__in=[4, 5]).values_list('user', flat=True))
                # for id in users_id:
                #     user = User.objects.get(id=id)
                #     remind = user.remind.last()
                #     remind_first = remind.remind_first
                #     remind_second = remind.remind_second
                #     print(id, remind_first, remind_second)

                #     time_zon = user.datetime_start.astimezone().tzinfo
                #     cur_time = datetime.now(time_zon)
                #     eating = user.day_food.filter(
                #         time__year=cur_time.year,
                #         time__month=cur_time.month,
                #         time__day=cur_time.day
                #     ).aggregate(Sum('calories')).get('calories__sum')
                #     norm = UserProgram.objects.filter(user=user).last().cur_dci

                #     res = send_remind(cur_time, eating, norm,
                #                       remind_first, remind_second)
                #     if not res is None:
                #         if res == 'send_second':
                #             template_send_message(
                #                 bot, user.id, 'remind_second')
                #             print(f'{user.id} не указал половину')
                #             remind.remind_second = True
                #             remind.remind_first = True
                #             remind.save()
                #         elif res == 'send_first':
                #             template_send_message(
                #                 bot, user.id, 'remind_first')
                #             print(f'{user.id} не указал')
                #             remind.remind_first = True
                #             remind.save()
                #         elif res == 'set_flag':
                #             remind.remind_second = False
                #             remind.remind_first = False
                #             remind.save()
                # if cur_time.time() > time(hour=19, minute=0, second=0) and (eating in (0, None) or eating < norm / 2) and remind_second == False:
                #     template_send_message(bot, user.id, 'remind_second')
                #     print(f'{user.id} не указал половину')
                #     remind.remind_second = True
                #     remind.remind_first = True
                #     remind.save()
                # elif cur_time.time() > time(hour=13, minute=0, second=0) and eating in (0, None) and remind_first == False:
                #     template_send_message(bot, user.id, 'remind_first')
                #     print(f'{user.id} не указал')
                #     remind.remind_first = True
                #     remind.save()
                # elif cur_time.time() < time(hour=1, minute=0, second=0) and (remind_second == True or remind_first == True):
                #     remind.remind_second = False
                #     remind.remind_first = False
                #     remind.save()
                # sleep(60*60)

        th = threading.Thread(target=bg_thread)
        th.daemon = True
        th.start()
        print('----------')
        print('начало бота')
        bot.infinity_polling(timeout=600)
        # while True:
        #     try:
        #         bot.polling(non_stop=True, timeout=600)
        #     except KeyboardInterrupt:
        #         exit(0)
        #     else:
        #         bot.stop_polling()
        #         sleep(3)
        # bot.polling(non_stop=True, timeout=600)
        print('конец бота')
        print('----------')
