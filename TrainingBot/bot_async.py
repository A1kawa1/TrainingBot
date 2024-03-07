from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext

from TrainingBot.wsgi import *
from TrainingBot.settings import TOKEN
from model.models import *
from bot.SqlQueryAsync import *
from bot.SendMessageAsync import *
from bot.InlineKeyboardAsync import *
from bot.ButtonAsync import *
from bot.FilterAsync import *
from bot.State import StateForm
from bot.config import TYPE


bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())


async def main():
    await dp.start_polling(bot)


@dp.message(Command('start'))
async def start(message: types.Message):
    id = message.chat.id
    first_name = message.chat.first_name
    last_name = message.chat.last_name
    username = message.chat.username
    date_start = message.date

    if id in await get_user('id'):
        await bot.send_message(
            chat_id=id,
            text=f'{first_name}, я вижу вы уже пользовались нашими услугами',
            reply_markup=await create_keyboard_stage(id)
        )
        return

    user = User(
        id=id,
        first_name=first_name,
        last_name=last_name,
        username=username,
        datetime_start=date_start
    )

    await user.asave()
    info_user = InfoUser(user=user)
    await info_user.asave()
    target_user = TargetUser(user=user)
    await target_user.asave()
    user_stage_guide = UserStageGuide(user=user)
    await user_stage_guide.asave()
    remind = RemindUser(user=user)
    await remind.asave()

    await template_send_message(bot, id, 'start')
    await template_send_message(bot, id, 'start_last')


@dp.message(StateForm.GET_AGE, FilterKeyboardButton())
async def get_age(message: types.Message, state: FSMContext):
    await change_info(message, 'age', state, bot)


@dp.message(StateForm.GET_HEIGHT, FilterKeyboardButton())
async def get_height(message: types.Message, state: FSMContext):
    await change_info(message, 'height', state, bot)


@dp.message(StateForm.GET_TARGET_WEIGHT, FilterKeyboardButton())
async def get_target_weight(message: types.Message, state: FSMContext):
    await change_target_weight(message, 'target_weight', state, bot)


@dp.message(StateForm.GET_CUR_WEIGHT, FilterKeyboardButton())
async def get_cur_weight(message: types.Message, state: FSMContext):
    await change_target_weight(message, 'cur_weight', state, bot)


@dp.message(StateForm.GET_CUR_DCI, FilterKeyboardButton())
async def get_cur_dci(message: types.Message, state: FSMContext):
    await change_cur_DCI(message, state, bot)


@dp.message(StateForm.GET_FOOD, FilterKeyboardButton())
async def get_new_food(message: types.Message, state: FSMContext):
    await get_food(message, state, bot)


@dp.message(StateForm.GET_NEW_DAY_DCI, FilterKeyboardButton())
async def get_new_day_dci(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    food_id = state_data.get('food_id')
    await change_day_DCI(message, food_id, state, bot)


@dp.message(StateForm.GET_NEW_WEIGHT, FilterKeyboardButton())
async def get_weight_in_program(message: types.Message, state: FSMContext):
    await change_weight_in_program(message, state, bot)


@dp.message(StateForm.GET_TIME_ZONE, FilterKeyboardButton())
async def get_user_tz(message: types.Message, state: FSMContext):
    await get_time_zone(message, state, bot)


@dp.message(StateForm.GET_NEW_WEEK_EATING, FilterKeyboardButton())
async def get_new_week_eating(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    eating_id = state_data.get('eating_id')
    await change_week_eating(message, eating_id, state, bot)


@dp.message(FilterGetCalories(bot), FilterKeyboardButton())
async def calories(message: types.Message):
    tmp = message.text.split()
    id_first = -1
    for i in range(len(tmp)):
        if tmp[i][0].isalpha():
            id_first = i
            break
    name = None

    if len(tmp) == 1:
        try:
            calories = eval(message.text)
        except:
            await bot.send_message(
                chat_id=message.from_user.id,
                text='Вводите согласно формату, повторите попытку',
            )
            return
        data = (calories, message.from_user.id)
    else:
        if id_first != -1:
            calories_data = ' '.join(tmp[:id_first])
            name = ' '.join(tmp[id_first:])
        else:
            calories_data = message.text

        try:
            data = (eval(calories_data),
                    message.from_user.id)
        except:
            await bot.send_message(
                chat_id=message.from_user.id,
                text=f'Простите, но мы не смогли распознать ваши данные'
            )
            return

    user = await User.objects.aget(id=data[1])
    food_user = UserDayFood(
        user=user,
        calories=data[0],
        name=name,
        time=await get_user_datetime(
            utc_datetime=message.date,
            user=user
        )
    )
    await food_user.asave()

    next_stage, calories = await update_result_day_DCI(message)

    text = await create_text_stage_4_5(calories, data[1])
    await bot.send_message(
        chat_id=data[1],
        text=text
    )
    await send_yesterday_remind(data[1], message, bot)

    if next_stage == 'dci_success':
        await update_stage_5(data[1], message, bot)
        return


@dp.message(F.text)
async def button_text(message: types.Message, state: FSMContext):
    try:
        await state.clear()
        id = message.chat.id

        if id not in await get_user('id'):
            print('not user')
            # start(message)
            '''


            хз че с областью видимости


            '''
        elif message.text == 'Сброс':
            ...
            # markup = telebot.types.InlineKeyboardMarkup()
            # markup.add(telebot.types.InlineKeyboardButton(
            #     text='Подтвердить',
            #     callback_data='delete_profile'
            # ))
            # markup.add(telebot.types.InlineKeyboardButton(
            #     text='Закрыть',
            #     callback_data='close'
            # ))
            # bot.send_message(
            #     chat_id=id,
            #     text='Подтвердите сброс аккаунта',
            #     reply_markup=markup
            # )
        elif message.text == 'Мои данные':
            await bot.send_message(
                chat_id=id,
                text='Укажите следующие данные',
                reply_markup=await create_InlineKeyboard_user_info(id)
            )
        elif message.text == 'Моя цель':
            await bot.send_message(
                chat_id=id,
                text='Давайте выберем, что вы хотите',
                reply_markup=await create_InlineKeyboard_target(message)
            )
        elif message.text == 'Завершить обучение':
            if await get_stage(id) > 2:
                return

            await update_stage(id, bot, 3)
        elif message.text == 'Я знаю сколько я ем сейчас':
            await bot.send_message(
                chat_id=id,
                text=(
                    'Укажите сколько калорий вы съедаете сейчас в сутки и '
                    'мы рассчитаем программу управления весом для '
                    'достижения достигнутой цели.'
                ),
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(
                        text='Закрыть',
                        callback_data='close'
                    )
                ]])
            )
            await state.set_state(StateForm.GET_CUR_DCI)
        elif message.text == 'Мастер обучения':
            keyboard, markup = await create_InlineKeyboard_guide(id)

            await bot.send_message(
                chat_id=id,
                text='Давайте же вспомним как считать калории.',
                reply_markup=keyboard
            )
            await bot.send_message(
                chat_id=id,
                text='Для этого пожалуйста перейдите по ссылке и ответьте на несколько простых вопросов.',
                reply_markup=markup
            )
        elif message.text == 'Я все вспомнил':
            await bot.send_message(
                chat_id=id,
                text='Поздравляем, вы вспомнили как считать калории.',
                reply_markup=await create_keyboard_stage(id)
            )
        elif message.text == 'Начать сбор данных':
            await update_stage_4(id, bot)
        elif message.text == 'Меню':
            await bot.send_message(
                chat_id=id,
                text='Выберите что вы поели',
                reply_markup=await create_InlineKeyboard_food(id)
            )
        elif message.text == 'Мониторинг':
            user_days_dci = ResultDayDci.objects.filter(user=id)
            count_day = await user_days_dci.acount()
            if count_day == 0:
                regularity = 0
            else:
                regularity = await user_days_dci.filter(~Q(calories=0)).acount()
                regularity = int(regularity / count_day * 100)

            data = user_days_dci.filter(~Q(calories=0)).order_by('date')
            len_data = await data.acount()

            calories = []
            if len_data == 0:
                avg_dci = 0
            elif len_data in (1, 2, 3):
                async for el in data:
                    calories.append(el.calories)

                if len_data in (1, 2):
                    avg_dci = calories[0]
                else:
                    avg_dci = calories[1]
            else:
                data_dci = []
                async for el in data[1:len_data-1]:
                    data_dci.append(el.calories)

                avg_dci = int(sum(data_dci) / len(data_dci))

            buttons = [
                [InlineKeyboardButton(
                    text=f'Дней мониторинга: {count_day}',
                    callback_data='asdasdf'
                )],
                [InlineKeyboardButton(
                    text=f'Регулярность ввода данных: {regularity}%',
                    callback_data='asdasdf'
                )],
                [InlineKeyboardButton(
                    text=f'Текущее кол-во калорий в день: {avg_dci}',
                    callback_data='asdasdf'
                )]
            ]
            await bot.send_message(
                chat_id=id,
                text='Мы еще не уверены сколько вы едите в день.\nТекущие показатели мониторинга следующие:',
                reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
            )

            buttons = [
                [InlineKeyboardButton(
                    text='Завершить мониторинг',
                    callback_data='end_monitoring'
                )],
                [InlineKeyboardButton(
                    text='Продолжить мониторинг',
                    callback_data='continue_monitoring'
                )]
            ]
            await bot.send_message(
                chat_id=id,
                text='Если вы хотите завершить мониторинг, то придется ввести текущее кол-во калорий вручную.',
                reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
            )
        elif message.text == 'Статистика за день':
            next_stage, calories = await update_result_day_DCI(message)
            text = await create_text_days_eating(calories, id)

            user = await User.objects.aget(id=id)
            date = await get_user_datetime(
                utc_datetime=message.date,
                user=user
            )
            await bot.send_message(
                chat_id=id,
                text=text,
                reply_markup=await create_InlineKeyboard_day_food(id, date)
            )

            if next_stage == 'dci_success':
                await update_stage_5(id, message, bot)
                return
        elif message.text == 'Моя программа':
            user = await User.objects.aget(id=id)
            cur_date = await get_user_datetime(
                utc_datetime=message.date,
                user=user
            )
            cur_date = cur_date.date()

            user_program = await user.program.alast()
            user_target = await user.target.alast()

            len_result_day_dci = await user.result_day_dci.filter(date=cur_date).acount()

            if len_result_day_dci == 0 and user_program.date_start != cur_date:
                user_program.cur_day = (
                    cur_date - user_program.date_start).days + 1
                await user_program.asave()

            await update_normal_dci(user, user_program, user_target, cur_date)

            day_result, create = await ResultDayDci.objects.aget_or_create(
                user=user,
                date=cur_date
            )

            if create == True:
                day_result.deficit = user_program.cur_dci

            await day_result.asave()
            await bot.send_message(
                chat_id=id,
                text=('Ваша программа'),
                reply_markup=await create_InlineKeyboard_program(id)
            )
        elif message.text == 'Статистика за неделю':
            user = await User.objects.aget(id=id)
            cur_date = await get_user_datetime(
                utc_datetime=message.date,
                user=user
            )
            cur_date = cur_date.date()

            await bot.send_message(
                chat_id=id,
                text='Приемы пищи за последние 7 дней',
                reply_markup=await create_InlineKeyboard_week_eating(user, message, cur_date)
            )

    except ObjectDoesNotExist:
        await bot.send_message(
            chat_id=id,
            text='Запись была удалена'
        )
    except Exception as e:
        print(e)
        await bot.send_message(
            chat_id=id,
            text='Неизвестная ошибка'
        )


@dp.callback_query()
async def callback_query(call: types.CallbackQuery, state: FSMContext):
    try:
        await state.clear()
        id = call.from_user.id
        if call.data == 'close':
            await bot.delete_message(
                chat_id=id,
                message_id=call.message.message_id
            )
        elif id not in await get_user('id'):
            # start(call.message)
            '''


            хз че с областью видимости


            '''
        elif call.data == 'get_time_zone':
            if await get_stage(id) != -1:
                await bot.send_message(
                    chat_id=id,
                    text='Давайте же продолжим работу',
                    reply_markup=await create_keyboard_stage(id)
                )
                return
            await bot.send_message(
                chat_id=id,
                text=('Для начала отправьте свой часовой пояс для дальнейшей корректной работы.'
                      '\nНапример: 0, 1, 2 и тд')
            )
            await state.set_state(StateForm.GET_TIME_ZONE)
        elif call.data == 'right_time_zone':
            if await get_stage(id) != -1:
                await bot.send_message(
                    chat_id=id,
                    text='Давайте же продолжим работу',
                    reply_markup=await create_keyboard_stage(id)
                )
                return

            user = await User.objects.aget(id=id)
            user.datetime_start = await get_user_datetime(
                utc_datetime=user.datetime_start,
                user=user
            )
            await user.asave()

            user_stage_guide = await UserStageGuide.objects.filter(user=user).alast()
            user_stage_guide.stage = 0
            await user_stage_guide.asave()

            await bot.send_message(
                chat_id=id,
                text='Отлично, теперь мы знаем ваш часовой пояс',
                reply_markup=await create_keyboard_stage(id)
            )
            await bot.send_message(
                chat_id=id,
                text='Давайте же продолжим работу',
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(
                        text='Продолжить',
                        callback_data='login'
                    )
                ]])
            )
        elif call.data == 'wrong_time_zone':
            if await get_stage(id) != -1:
                await bot.send_message(
                    chat_id=id,
                    text='Давайте же продолжим работу',
                    reply_markup=await create_keyboard_stage(id)
                )
                return

            await bot.send_message(
                chat_id=id,
                text=('Давайте попробуем еще раз, отправьте свой часовой пояс.'
                      '\nНапример: 0, 1, 2 и тд')
            )
            await state.set_state(StateForm.GET_TIME_ZONE)
        elif call.data == 'login':
            if await get_stage(id) != 0:
                await bot.send_message(
                    chat_id=id,
                    text='Давайте же продолжим работу',
                    reply_markup=await create_keyboard_stage(id)
                )
                return

            await template_send_message(bot, id, 'stage0')
            await bot.send_message(
                chat_id=id,
                text='Укажите следующие данные',
                reply_markup=await create_InlineKeyboard_user_info(id)
            )
        elif call.data in ['change_height', 'change_age']:
            buttons = [[
                InlineKeyboardButton(
                    text='Назад',
                    callback_data='my_info'
                ),
                InlineKeyboardButton(
                    text='Закрыть',
                    callback_data='close'
                )
            ]]
            TEXT_FUNC = {
                'change_age': ['возраст', StateForm.GET_AGE],
                'change_height': ['рост (см)', StateForm.GET_HEIGHT],
            }
            text = f'Укажите свой {TEXT_FUNC[call.data][0]}'
            await bot.edit_message_text(
                chat_id=id,
                message_id=call.message.message_id,
                text=text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
            )

            await state.set_state(TEXT_FUNC[call.data][1])
        elif call.data == 'change_gender':
            await bot.edit_message_text(
                chat_id=id,
                message_id=call.message.message_id,
                text='Укажите свой пол',
                reply_markup=await create_InlineKeyboard_gender()
            )
        elif call.data == 'my_info':
            await bot.edit_message_text(
                chat_id=id,
                message_id=call.message.message_id,
                text='Укажите следующие данные',
                reply_markup=await create_InlineKeyboard_user_info(id)
            )
        elif call.data in ['men', 'woomen']:
            await get_gender(call, bot)
        elif call.data == 'create_target':
            await bot.send_message(
                chat_id=id,
                text='Давайте выберем, что вы хотите',
                reply_markup=await create_InlineKeyboard_target(call.message)
            )
        elif call.data in TYPE:
            target_user = await TargetUser.objects.filter(user=id).alast()
            target_user.type = call.data
            await target_user.asave()

            await bot.edit_message_text(
                chat_id=id,
                message_id=call.message.message_id,
                text='Укажите следующие данные',
                reply_markup=await create_InlineKeyboard_target(call.message)
            )
        elif call.data == 'my_target':
            target = await TargetUser.objects.filter(user=id).alast()
            target.type = None
            await target.asave()

            await bot.edit_message_text(
                chat_id=id,
                message_id=call.message.message_id,
                text='Давайте выберем, что вы хотите',
                reply_markup=await create_InlineKeyboard_target(call.message)
            )
        elif call.data in ['change_target', 'change_weight']:
            buttons = [[
                InlineKeyboardButton(
                    text='Назад',
                    callback_data='my_cur_target'
                ),
                InlineKeyboardButton(
                    text='Закрыть',
                    callback_data='close'
                )
            ]]
            TEXT_FUNC = {
                'change_target': ['новую цель (кг)', StateForm.GET_TARGET_WEIGHT],
                'change_weight': ['текущий вес (кг)', StateForm.GET_CUR_WEIGHT]
            }
            text = f'Укажите {TEXT_FUNC[call.data][0]}'
            await bot.edit_message_text(
                chat_id=id,
                message_id=call.message.message_id,
                text=text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
            )

            await state.set_state(TEXT_FUNC[call.data][1])
        elif call.data == 'change_activity':
            await bot.edit_message_text(
                chat_id=id,
                message_id=call.message.message_id,
                text='Выберите новую активность',
                reply_markup=await create_InlineKeyboard_activity()
            )
        elif call.data in ACTIVITY.keys():
            await get_activity(call, bot)
        elif call.data == 'my_cur_target':
            await bot.edit_message_text(
                chat_id=id,
                message_id=call.message.message_id,
                text='Укажите следующие данные',
                reply_markup=await create_InlineKeyboard_target(call.message)
            )
        elif call.data == 'start_guide':
            keyboard, markup = await create_InlineKeyboard_guide(id)
            await bot.send_message(
                chat_id=id,
                text='Давайте же начнем обучение.',
                reply_markup=keyboard
            )
            await bot.send_message(
                chat_id=id,
                text='Для его прохождение пожалуйста перейдите по ссылке и ответьте на несколько простых вопросов.',
                reply_markup=markup
            )
        elif call.data == 'skip_guide':
            if await get_stage(id) > 2:
                await bot.send_message(
                    chat_id=id,
                    text='Поздравляем, вы вспомнили как считать калории.',
                    reply_markup=await create_keyboard_stage(id)
                )
                return

            await update_stage(id, bot, 3)
        elif call.data == 'skip_guide_stage_2':
            if await get_stage(id) > 2:
                return

            await update_stage(id, bot, 3)
        elif call.data in ['get_cur_DCI', 'end_monitoring']:
            if call.data == 'get_cur_DCI' and await get_stage(id) != 3:
                return

            if call.data == 'end_monitoring' and await get_stage(id) != 4:
                return

            await bot.send_message(
                chat_id=id,
                text=(
                    'Укажите сколько калорий вы съедаете сейчас в сутки и '
                    'мы рассчитаем программу управления весом для '
                    'достижения достигнутой цели.'
                ),
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(
                        text='Закрыть',
                        callback_data='close'
                    )
                ]])
            )
            await state.set_state(StateForm.GET_CUR_DCI)
        elif call.data == 'start_get_cur_DCI':
            await update_stage_4(id, bot)
        elif call.data == 'add_food':
            buttons = [[
                InlineKeyboardButton(
                    text='Назад',
                    callback_data='back_menu_main'
                ),
                InlineKeyboardButton(
                    text='Закрыть',
                    callback_data='close'
                )
            ]]
            await bot.edit_message_text(
                chat_id=id,
                message_id=call.message.message_id,
                text='Отправьте название и каллорийность\nв виде: кКл блюдо\n(несколько блюд вводите с новой строки)',
                reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
            )
            await state.set_state(StateForm.GET_FOOD)
        elif call.data.startswith('back_menu_main'):
            await bot.edit_message_text(
                chat_id=id,
                message_id=call.message.message_id,
                text='Выберите что вы поели',
                reply_markup=await create_InlineKeyboard_food(id)
            )
        elif call.data.startswith('food_'):
            await add_from_menu_day_DCI(call, bot)
        elif call.data == 'continue_monitoring':
            await bot.send_message(
                chat_id=id,
                text='Тогда давайте продолжим'
            )
        elif call.data.startswith('detail_'):
            _, food_id = call.data.split('_')

            food = await UserDayFood.objects.aget(id=food_id)
            if food.name is None:
                text = (f'{food.time.hour}:{food.time.minute} '
                        f'- {food.calories}кКл')
            else:
                text = (f'{food.time.hour}:{food.time.minute} '
                        f'- {food.name} {food.calories}кКл')

            await bot.edit_message_text(
                chat_id=id,
                message_id=call.message.message_id,
                text=text,
                reply_markup=await create_InlineKeyboard_detail_day_food(food_id)
            )
        elif call.data.startswith('delete_day_dci_'):
            food_id = call.data[15:]
            food = await UserDayFood.objects.aget(id=food_id)
            cal_delete = food.calories
            await food.adelete()

            next_stage, calories = await update_result_day_DCI(call.message)

            await bot.edit_message_text(
                chat_id=id,
                message_id=call.message.message_id,
                text=f'Вы удалили {cal_delete}кКл'
            )
            text = await create_text_days_eating(calories, id)
            user = await User.objects.aget(id=id)
            date = await get_user_datetime(
                utc_datetime=call.message.date,
                user=user
            )
            await bot.send_message(
                chat_id=id,
                text=text,
                reply_markup=await create_InlineKeyboard_day_food(id, date)
            )

            if next_stage == 'dci_success':
                await update_stage_5(id, call.message, bot)
                return
        elif call.data.startswith('change_day_dci_'):
            await bot.edit_message_text(
                chat_id=id,
                message_id=call.message.message_id,
                text='Введите новые данные\nв виде - кКл блюдо',
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(
                        text='Закрыть',
                        callback_data='close'
                    )
                ]])
            )
            food_id = call.data[15:]
            await state.set_state(StateForm.GET_NEW_DAY_DCI)
            await state.set_data({'food_id': food_id})
        elif call.data == 'back_day_food':
            next_stage, calories = await update_result_day_DCI(call.message)
            text = await create_text_days_eating(calories, id)
            user = await User.objects.aget(id=id)
            date = await get_user_datetime(
                utc_datetime=call.message.date,
                user=user
            )
            await bot.edit_message_text(
                chat_id=id,
                message_id=call.message.message_id,
                text=text,
                reply_markup=await create_InlineKeyboard_day_food(id, date)
            )

            if next_stage == 'dci_success':
                await update_stage_5(id, call.message, bot)
                return
        elif call.data == 'change_weight_in_program':
            await bot.edit_message_text(
                chat_id=id,
                message_id=call.message.message_id,
                text='Укажите ваш текущий вес',
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(
                        text='Закрыть',
                        callback_data='close'
                    )
                ]])
            )
            await state.set_state(StateForm.GET_NEW_WEIGHT)
        elif call.data.startswith('edit_week_eating_'):
            eating_id = int(call.data[17:])
            record = await ResultDayDci.objects.aget(id=eating_id)
            date = record.date

            await bot.edit_message_text(
                chat_id=id,
                message_id=call.message.message_id,
                text=f'{date.strftime("%d:%m:%Y")}\nВведите новое количество калорий',
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(
                        text='Закрыть',
                        callback_data='close'
                    )
                ]])
            )

            await state.set_state(StateForm.GET_NEW_WEEK_EATING)
            await state.set_data({'eating_id': eating_id})

    except ObjectDoesNotExist:
        await bot.send_message(
            chat_id=id,
            text='Запись была удалена'
        )
    except Exception as e:
        print(e)
        await bot.send_message(
            chat_id=id,
            text='Неизвестная ошибка'
        )

if __name__ == '__main__':
    print('start bot')
    asyncio.run(main())
