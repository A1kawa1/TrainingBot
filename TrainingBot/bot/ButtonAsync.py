from django.db.models import Sum
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, timedelta
import telebot

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
        await message.answer(
            text='Вводите целое число, повторите попытку'
        )
        return
    if int(message.text) <= 0:
        await message.answer(
            text='Вводите положительное число, повторите попытку'
        )
        return

    info_user = await InfoUser.objects.aget(user=id)
    if field == 'age':
        info_user.age = int(message.text)
    elif field == 'height':
        info_user.height = int(message.text)
    await info_user.asave()

    await change_DCI_ideal_weight(message)
    await state.clear()

    await message.answer(
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
            chat_id=message.chat.id,
            text='Вводите целое или дробное число, повторите попытку',
        )
        return
    if weight <= 0:
        await bot.send_message(
            chat_id=message.chat.id,
            text='Вводите положительное число, повторите попытку',
        )
        return

    target_user = await TargetUser.objects.filter(user=id).alast()
    if field == 'target_weight':
        target_user.target_weight = round(weight, 1)
    elif field == 'cur_weight':
        target_user.cur_weight = round(weight, 1)
    await target_user.asave()

    await change_DCI_ideal_weight(message)
    await state.clear()

    markup = await create_InlineKeyboard_target(message)

    if (all([target_user.cur_weight, target_user.target_weight])
        and ('None' not in (target_user.type, target_user.activity))
            and await get_stage(id) == 1):
        if target_user.cur_weight <= target_user.target_weight:
            await bot.send_message(
                chat_id=id,
                text='Пожалуйста укажите коректный текущий вес и цель',
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
                text='Пожалуйста укажите коректный текущий вес и цель',
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
            text='Вводите целое число, повторите попытку'
        )
        return
    if int(message.text) <= 0:
        bot.send_message(
            chat_id=id,
            text='Вводите положительное число, повторите попытку'
        )
        return

    target_user = await TargetUser.objects.filter(user=id).alast()
    target_user.cur_dci = int(message.text)
    await target_user.asave()

    await state.clear()

    if await get_stage(id) in (3, 4):
        await update_stage_5(id, message, bot)
        return

    await bot.send_message(
        chat_id=id,
        text='Вы изменили текущий DCI'
    )


async def create_program(id, message, for_cur_target=False):
    cur_date = message.date

    user = await User.objects.aget(id=id)
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


async def update_stage(id, bot, stage):
    user_stage_guide = await UserStageGuide.objects.aget(user=id)
    user_stage_guide.stage = stage
    await user_stage_guide.asave()

    await template_send_message(bot, id, f'stage{stage}')
    await template_send_message(bot, id, f'stage{stage}_last')


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
