from datetime import timedelta, datetime, timezone
from django.db.models import Sum
from django.core.exceptions import ObjectDoesNotExist

from bot.InlineKeyboardAsync import *
from bot.config import *
from bot.SendMessageAsync import *
from model.models import *


async def check_int(x):
    try:
        y = int(x)
        return True
    except:
        return False


async def check_float(x):
    try:
        x = x.replace(',', '.')
        y = float(x)
        return y
    except:
        return False


async def get_user_datetime(offset=None, utc_datetime=None, user=None):
    if utc_datetime is None:
        return datetime.now(timezone(timedelta(hours=offset)))
    else:
        offset = user.offset
        return utc_datetime + timedelta(hours=offset)


async def get_time_zone(message, state, bot):
    id = message.chat.id

    if not await check_int(message.text):
        await bot.send_message(
            chat_id=id,
            text='Вводите целое число, повторите попытку'
        )
        return

    if int(message.text) <= 0:
        await bot.send_message(
            chat_id=id,
            text='Вводите положительное число, повторите попытку'
        )
        return

    await state.clear()

    user = await User.objects.aget(id=id)
    user.offset = int(message.text)
    await user.asave()

    cur_time = await get_user_datetime(offset=int(message.text))
    cur_time = cur_time.strftime("%d.%m %H:%M")
    buttons = [[
        InlineKeyboardButton(
            text='Да',
            callback_data='right_time_zone'
        ),
        InlineKeyboardButton(
            text='Нет',
            callback_data='wrong_time_zone'
        )
    ]]

    await bot.send_message(
        chat_id=id,
        text=f'У вас сейчас {cur_time}?',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


async def get_ideal_DCI(inf):
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


async def change_DCI_ideal_weight(message):
    id = message.chat.id

    user = await User.objects.aget(id=id)
    info_user = await user.info.alast()
    target_user = await user.target.alast()
    inf = (
        info_user.age,
        info_user.height,
        target_user.cur_weight,
        info_user.gender,
        target_user.activity
    )
    if (None not in inf) and ('None' not in inf):
        DCI = await get_ideal_DCI(inf)
        target_user.dci = DCI
        await target_user.asave()

    if inf[3] != 'None' and inf[1] != 0:
        if inf[3] == 'woomen':
            ideal_weight = (3.5 * inf[1] / 2.54 - 108) * 0.453
        else:
            ideal_weight = (4 * inf[1] / 2.54 - 128) * 0.453

        info_user.ideal_weight = round(ideal_weight, 1)
        await info_user.asave()


async def change_info(message, field, state, bot):
    id = message.chat.id

    if not await check_int(message.text):
        await bot.send_message(
            chat_id=id,
            text='Вводите целое число, повторите попытку',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(
                    text='Закрыть',
                    callback_data='close'
                )
            ]])
        )
        return

    if int(message.text) <= 0:
        await bot.send_message(
            chat_id=id,
            text='Вводите положительное число, повторите попытку',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(
                    text='Закрыть',
                    callback_data='close'
                )
            ]])
        )
        return

    await state.clear()

    info_user = await InfoUser.objects.aget(user=id)
    if field == 'age':
        info_user.age = int(message.text)
    elif field == 'height':
        info_user.height = int(message.text)
    await info_user.asave()

    await change_DCI_ideal_weight(message)

    await bot.send_message(
        chat_id=id,
        text='Укажите следующие данные',
        reply_markup=await create_InlineKeyboard_user_info(id)
    )

    if (all([info_user.age, info_user.height])
        and info_user.gender != 'None'
            and await get_stage(id) == 0):
        await update_stage(id, bot, 1)


async def get_gender(call, bot):
    id = call.message.chat.id

    info_user = await InfoUser.objects.aget(user=id)
    info_user.gender = call.data
    await info_user.asave()

    await change_DCI_ideal_weight(call.message)

    await bot.edit_message_text(
        chat_id=id,
        message_id=call.message.message_id,
        text='Укажите следующие данные',
        reply_markup=await create_InlineKeyboard_user_info(id)
    )

    if (all([info_user.age, info_user.height])
        and info_user.gender != 'None'
            and await get_stage(id) == 0):
        await update_stage(id, bot, 1)


async def change_target_weight(message, field, state, bot):
    id = message.chat.id
    weight = await check_float(message.text)

    if not weight:
        await bot.send_message(
            chat_id=id,
            text='Вводите целое или дробное число, повторите попытку',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(
                    text='Закрыть',
                    callback_data='close'
                )
            ]])
        )
        return

    if weight <= 0:
        await bot.send_message(
            chat_id=id,
            text='Вводите положительное число, повторите попытку',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(
                    text='Закрыть',
                    callback_data='close'
                )
            ]])
        )
        return

    await state.clear()

    target_user = await TargetUser.objects.filter(user=id).alast()
    if field == 'target_weight':
        target_user.target_weight = round(weight, 1)
    elif field == 'cur_weight':
        target_user.cur_weight = round(weight, 1)
    await target_user.asave()

    await change_DCI_ideal_weight(message)

    markup = await create_InlineKeyboard_target(message)

    if (all([target_user.cur_weight, target_user.target_weight])
        and ('None' not in (target_user.type, target_user.activity))
            and await get_stage(id) == 1):
        if target_user.cur_weight <= target_user.target_weight:
            await bot.send_message(
                chat_id=id,
                text='Пожалуйста укажите корректный текущий вес и цель',
                reply_markup=markup
            )
            return
        await bot.send_message(
            chat_id=id,
            text='Укажите следующие данные',
            reply_markup=markup
        )
        await update_stage(id, bot, 2)
    else:
        await bot.send_message(
            chat_id=id,
            text='Укажите следующие данные',
            reply_markup=markup
        )


async def get_activity(call, bot):
    id = call.message.chat.id

    target_user = await TargetUser.objects.filter(user=id).alast()
    target_user.activity = call.data
    await target_user.asave()

    await change_DCI_ideal_weight(call.message)

    markup = await create_InlineKeyboard_target(call.message)

    if (all([target_user.cur_weight, target_user.target_weight])
        and ('None' not in [target_user.type, target_user.activity])
            and await get_stage(id) == 1):
        if target_user.cur_weight <= target_user.target_weight:
            await bot.edit_message_text(
                chat_id=id,
                message_id=call.message.message_id,
                text='Пожалуйста укажите корректный текущий вес и цель',
                reply_markup=markup
            )
            return
        await bot.edit_message_text(
            chat_id=id,
            message_id=call.message.message_id,
            text='Укажите следующие данные',
            reply_markup=markup
        )
        await update_stage(id, bot, 2)
    else:
        await bot.edit_message_text(
            chat_id=id,
            message_id=call.message.message_id,
            text='Укажите следующие данные',
            reply_markup=markup
        )


async def change_cur_DCI(message, state, bot):
    id = message.chat.id

    if not await check_int(message.text):
        await bot.send_message(
            chat_id=id,
            text='Вводите целое число, повторите попытку',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(
                    text='Закрыть',
                    callback_data='close'
                )
            ]])
        )
        return

    if int(message.text) <= 0:
        await bot.send_message(
            chat_id=id,
            text='Вводите положительное число, повторите попытку',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(
                    text='Закрыть',
                    callback_data='close'
                )
            ]])
        )
        return

    await state.clear()

    target_user = await TargetUser.objects.filter(user=id).alast()
    target_user.cur_dci = int(message.text)
    await target_user.asave()

    if await get_stage(id) in (3, 4):
        await update_stage_5(id, message, bot)
        return

    await bot.send_message(
        chat_id=id,
        text='Вы изменили текущий DCI'
    )


async def create_program(id, message, for_cur_target=False):
    user = await User.objects.aget(id=id)
    cur_date = await get_user_datetime(
        utc_datetime=message.date,
        user=user
    )

    target = await user.target.alast()
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

    if for_cur_target:
        cur_program = await user.program.alast()
        cur_weight = cur_program.cur_weight
        cur_program.date_start = cur_date
        cur_program.start_dci = cur_dci
        cur_program.cur_dci = cur_dci_tmp
        cur_program.phase1 = phase1
        cur_program.phase2 = phase2
        cur_program.cur_day = 1
        cur_program.cur_weight = cur_weight
        cur_program.achievement = int((
            (target.cur_weight - cur_weight) /
            (target.cur_weight - target.target_weight)
        ) * 100)
        await cur_program.asave()
        return

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

    await program.asave()

    target.program = program
    await target.asave()


async def get_food(message, state, bot):
    id = message.chat.id

    foods = message.text.split('\n')

    count_success = 0
    for el in foods:
        id_space = el.find(' ')
        if id_space == -1:
            calories = el
            name = None
        else:
            calories = el[:id_space]
            name = el[id_space+1:].strip()

        if not await check_int(calories):
            continue

        count_success += 1
        user = await User.objects.aget(id=id)
        await UserFood.objects.aget_or_create(
            user=user,
            name=name,
            calories=calories
        )

    if not count_success:
        await bot.send_message(
            chat_id=id,
            text='Мы не смогли распознать ни одного блюда. Попробуйте еще раз',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(
                    text='Закрыть',
                    callback_data='close'
                )
            ]])
        )
        return
    else:
        await state.clear()

        await bot.send_message(
            chat_id=id,
            text='Блюдо добавлено'
        )
    await bot.send_message(
        chat_id=id,
        text='Выберите что вы поели',
        reply_markup=await create_InlineKeyboard_food(id)
    )


async def send_yesterday_remind(id, message, bot):
    if await get_stage(id) == 5:
        user = await User.objects.aget(id=id)
        cur_time = await get_user_datetime(
            utc_datetime=message.date,
            user=user
        )

        len_day_food = await user.day_food.filter(
            time__year=cur_time.year,
            time__month=cur_time.month,
            time__day=cur_time.day
        ).acount()

        if len_day_food == 1:
            result_day_dci = user.result_day_dci
            if await result_day_dci.all().acount() >= 2:
                res = await result_day_dci.aget(
                    date=cur_time.date()-timedelta(days=1))

                deficit = res.deficit
                result = res.calories

                if result == 0:
                    await template_send_message(
                        bot, id, 'yesterday_non_calories')
                    return
                elif deficit > 0:
                    mes = await Message.objects.filter(mesKey='yesterday_deficit').alast()
                    mes = mes.message + f' Вы сэкономили {deficit} калорий'
                else:
                    mes = await Message.objects.filter(mesKey='yesterday_proficit').alast()
                    mes = mes.message + f' Вы переели на {-deficit} калорий'

                await bot.send_message(
                    chat_id=id,
                    text=mes
                )


async def get_normal_dci(id, phase1, cur_day):
    user = await User.objects.aget(id=id)
    user_target = await user.target.alast()

    if cur_day > phase1:
        return user_target.dci * (1 - user_target.percentage_decrease / 100)
    else:
        if cur_day % 7 == 0:
            number_week = cur_day // 7
        else:
            number_week = cur_day // 7 + 1
        tmp = user_target.cur_dci - 100 * number_week
        if tmp < user_target.dci:
            tmp = user_target.dci
        return tmp


async def update_normal_dci(user, user_program, user_target, cur_date):
    dci = user_target.dci

    if ((user_program.cur_day - user_program.phase1) == 1
            and user_program.cur_dci != int(dci * (1 - user_target.percentage_decrease / 100))):
        user_program.cur_dci = await get_normal_dci(
            user.id, user_program.phase1, user_program.cur_day)
    else:
        len_result_day_dci = await user.result_day_dci.filter(date=cur_date).acount()
        if (len_result_day_dci == 0
            and user_program.cur_day != 1
                and user_program.phase1 != 0):
            user_program.cur_dci = await get_normal_dci(
                user.id, user_program.phase1, user_program.cur_day)

    await user_program.asave()


async def analise_data(data):
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


async def create_data_to_analise(id):
    data = ResultDayDci.objects.filter(user=id).order_by(
        'date').values_list('calories', 'date')

    calories = []
    date = []
    async for el in data:
        calories.append(el[0])
        date.append(el[1])

    if len(data) < 5:
        return False

    calories.pop(0)
    calories.pop()
    date.pop(0)
    date.pop()

    res_calories = []

    for index in range(len(date)-1):
        res_calories.append(calories[index])
        days_delta = date[index+1] - date[index]
        if days_delta != timedelta(days=1):
            res_calories.extend([0]*(days_delta.days-1))

    res_calories.append(calories[-1])
    return res_calories


async def check_variance(id):
    data = await create_data_to_analise(id)
    if not data:
        print('мало данных')
        return (False, None)

    return await analise_data(data)


async def update_result_day_DCI(message):
    id = message.chat.id
    user = await User.objects.aget(id=id)
    cur_time = await get_user_datetime(
        utc_datetime=message.date,
        user=user
    )
    remind = await user.remind.alast()

    calories = await user.day_food.filter(
        time__year=cur_time.year,
        time__month=cur_time.month,
        time__day=cur_time.day
    ).aaggregate(Sum('calories'))

    if calories.get('calories__sum') is None:
        calories['calories__sum'] = 0

    if calories.get('calories__sum') != 0:
        remind.remind_first = False
        await remind.asave()

    cur_date = cur_time.date()

    user_target = await user.target.alast()

    if await get_stage(id) == 5:
        user_program = await user.program.alast()

        if calories.get('calories__sum') > user_program.cur_dci / 2:
            remind.remind_second = False
            await remind.asave()

        len_result_day_dci = await user.result_day_dci.filter(date=cur_date).acount()
        if len_result_day_dci == 0 and user_program.date_start != cur_date:
            user_program.cur_day = (
                cur_date - user_program.date_start).days + 1
            await user_program.asave()

        await update_normal_dci(user, user_program, user_target, cur_date)

    result_dci, _ = await ResultDayDci.objects.aget_or_create(
        user=user,
        date=cur_date
    )

    if await get_stage(id) == 4:
        norm = user_target.dci
    else:
        norm = user_program.cur_dci

    result_dci.calories = calories.get('calories__sum')
    result_dci.deficit = norm - calories.get('calories__sum')
    await result_dci.asave()

    if await get_stage(id) == 4:
        tmp_res = await check_variance(id)
        if tmp_res[0]:
            user_target.cur_dci = tmp_res[1]
            await user_target.asave()
            print('dci определено')
            return 'dci_success', result_dci.calories

    return None, result_dci.calories


async def create_text_stage_4_5(calories, id):
    text = f'Сегодня вы поели на {calories}'
    if await get_stage(id) == 5:
        user = await User.objects.aget(id=id)
        user_program = await user.program.alast()
        calories_norm = user_program.cur_dci

        calories_last = calories_norm - calories
        if calories / calories_norm * 100 > 100 - K_MESSAGE_DANGER:
            text = f'Сегодня вы поели на {calories}\nОсталось {calories_last}'
            if calories_last < 0:
                text = (f'Сегодня вы поели на {calories}'
                        f'\nВы переели на {-calories_last}')

    return text


async def create_text_days_eating(calories, id):
    text = f'Сегодня вы поели на {calories}'
    if await get_stage(id) == 5:
        user = await User.objects.aget(id=id)
        user_program = await user.program.alast()
        calories_norm = user_program.cur_dci

        calories_last = calories_norm - calories
        text = f'Сегодня вы поели на {calories}\nОсталось {calories_last}'
        if calories_last < 0:
            text = (f'Сегодня вы поели на {calories}'
                    f'\nВы переели на {-calories_last}')

    return text


async def add_from_menu_day_DCI(call, bot):
    name = None
    msg = call.data[5:]
    name, calories = msg.split('_')
    if name == 'None':
        name = None

    id = call.message.chat.id
    user = await User.objects.aget(id=id)

    cur_date = await get_user_datetime(
        utc_datetime=call.message.date,
        user=user
    )

    data = (int(calories), id, cur_date)

    food_user = UserDayFood(
        user=user,
        name=name,
        calories=data[0],
        time=data[2]
    )
    await food_user.asave()

    next_stage, calories = await update_result_day_DCI(call.message)

    text = f'{name} - {data[0]}' if not name is None else f'{data[0]}'
    await bot.send_message(
        chat_id=data[1],
        text=text
    )

    text = await create_text_stage_4_5(calories, data[1])
    await bot.send_message(
        chat_id=data[1],
        text=text
    )
    await send_yesterday_remind(data[1], call.message, bot)

    if next_stage == 'dci_success':
        await update_stage_5(data[1], call.message, bot)
        return


async def change_day_DCI(message, food_id, state, bot):
    try:
        id = message.chat.id
        food = await UserDayFood.objects.aget(id=food_id)

        tmp = message.text.split()

        if not await check_int(tmp[0]):
            await bot.send_message(
                chat_id=id,
                text='Вводите целое число, повторите попытку',
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(
                        text='Закрыть',
                        callback_data='close'
                    )
                ]])
            )
            return

        if int(tmp[0]) <= 0:
            await bot.send_message(
                chat_id=id,
                text='Вводите положительное число, повторите попытку',
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(
                        text='Закрыть',
                        callback_data='close'
                    )
                ]])
            )
            return

        await state.clear()

        food.calories = int(tmp[0])
        if len(tmp) > 1:
            food.name = ' '.join(tmp[1:])

        await food.asave()

        next_stage, calories = await update_result_day_DCI(message)

        await bot.send_message(
            chat_id=id,
            text='Вы изменили данные'
        )

        text = await create_text_days_eating(calories, id)

        user = await User.objects.aget(id=id)

        cur_date = await get_user_datetime(
            utc_datetime=message.date,
            user=user
        )

        await bot.send_message(
            chat_id=id,
            text=text,
            reply_markup=await create_InlineKeyboard_day_food(id, cur_date)
        )

        if next_stage == 'dci_success':
            await update_stage_5(id, message, bot)
            return

    except ObjectDoesNotExist:
        await bot.send_message(
            chat_id=id,
            text='Запись была удалена'
        )
    except Exception:
        await bot.send_message(
            chat_id=id,
            text='Неизвестная ошибка'
        )


async def change_weight_in_program(message, state, bot):
    id = message.chat.id

    weight = await check_float(message.text)
    if not weight:
        await bot.send_message(
            chat_id=id,
            text='Вводите целое или дробное число, повторите попытку',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(
                    text='Закрыть',
                    callback_data='close'
                )
            ]])
        )
        return

    if weight <= 0:
        await bot.send_message(
            chat_id=id,
            text='Вводите положительное число, повторите попытку',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(
                    text='Закрыть',
                    callback_data='close'
                )
            ]])
        )
        return

    await state.clear()

    user = await User.objects.aget(id=id)
    target_user = await user.target.alast()

    program_user = await UserProgram.objects.filter(target=target_user).alast()
    program_user.cur_weight = round(weight, 1)

    program_user.achievement = int((
        (target_user.cur_weight - program_user.cur_weight) /
        (target_user.cur_weight - target_user.target_weight)
    ) * 100)
    await program_user.asave()

    cur_date = await get_user_datetime(
        utc_datetime=message.date,
        user=user
    )

    day_result, create = await ResultDayDci.objects.aget_or_create(
        user=user,
        date=cur_date
    )

    day_result.cur_weight = round(weight, 1)

    if create == True:
        day_result.deficit = program_user.cur_dci
    await day_result.asave()

    await bot.send_message(
        chat_id=id,
        text='Ваша программа',
        reply_markup=await create_InlineKeyboard_program(id)
    )

    if program_user.achievement >= 100:
        await template_send_message(bot, id, 'target_achieved')
        target_user.achieved = True
        await target_user.save()


async def update_stage(id, bot, stage):
    user_stage_guide = await UserStageGuide.objects.aget(user=id)
    user_stage_guide.stage = stage
    await user_stage_guide.asave()

    await template_send_message(bot, id, f'stage{stage}')
    await template_send_message(bot, id, f'stage{stage}_last')


async def update_stage_4(id, bot):
    user_stage_guide = await UserStageGuide.objects.aget(user=id)
    user_stage_guide.stage = 4
    await user_stage_guide.asave()

    await bot.send_message(
        chat_id=id,
        text='Начинаем фиксировать данные, не забывайте фиксировать каждый прием пищи.',
        reply_markup=await create_keyboard_stage(id)
    )


async def update_stage_5(id, message, bot):
    user_stage_guide = await UserStageGuide.objects.aget(user=id)
    user_stage_guide.stage = 5
    await user_stage_guide.asave()

    await create_program(id, message)

    await template_send_message(bot, id, 'stage5')

    await bot.send_message(
        chat_id=id,
        text='Ваша программа',
        reply_markup=await create_InlineKeyboard_program(id)
    )
