from datetime import time, datetime, timezone
from django.db.models import Q

from model.models import *
from bot.auxiliary import *
from bot.InlineKeyboardAsync import create_keyboard_stage, last_message


async def template_send_message(bot, chat_id, key):
    messages = Message.objects.filter(mesKey=key).order_by('order')
    if '_last' in key:
        try:
            messages = await messages.afirst()
            await bot.send_message(
                chat_id=chat_id,
                text=messages.message,
                reply_markup=await last_message(key)
            )
        except:
            ...
    else:
        async for mes in messages:
            try:
                await bot.send_message(
                    chat_id=chat_id,
                    text=mes.message,
                    reply_markup=await create_keyboard_stage(chat_id)
                )
            except Exception as e:
                print(e)


async def send_remind(bot):
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

    async for remind in reminds:
        try:
            user = remind.user
            remind = await user.remind.alast()
            cur_time = await get_user_datetime(
                utc_datetime=datetime.now(timezone.utc),
                user=user
            )
            res = await check_remind(cur_time, user)

            if res == 'send_weight':
                await template_send_message(bot, user.id, 'remind_weight')
                remind.day_without_indication_weight = 1
                remind.remind_weight = False
                await remind.asave()
            elif res == 'send_first':
                await template_send_message(bot, user.id, 'remind_first')
                remind.remind_first = False
                await remind.asave()
                cur_date = cur_time.date()
                day_result, create = await ResultDayDci.objects.aget_or_create(
                    user=user,
                    date=cur_date
                )

                if create == True:
                    target_user = await user.target.alast()
                    program_user = await UserProgram.objects.filter(target=target_user).alast()

                    program_user.cur_dci = await get_normal_dci(user.id, program_user.phase1, program_user.cur_day)
                    await program_user.asave()

                    day_result.deficit = program_user.cur_dci
                    if program_user.date_start != cur_date:
                        program_user.cur_day = (
                            cur_date - program_user.date_start).days + 1
                        await program_user.asave()

                    await day_result.asave()
            elif res == 'send_second':
                await template_send_message(bot, user.id, 'remind_second')
                remind.remind_second = False
                await remind.asave()

            if (cur_time.time() < time(hour=9, minute=0, second=0)
                    and (remind.remind_second == False or remind.remind_first == False or remind.remind_weight == False)):
                remind.remind_first = True
                remind.remind_second = True
                remind.remind_weight = True

                if remind.day_without_indication_weight == 0:
                    remind.day_without_indication_weight = 1

                await remind.asave()
        except:
            ...

    async for set_flag in set_flags:
        try:
            user = set_flag.user
            remind = await user.remind.alast()
            cur_time = await get_user_datetime(
                utc_datetime=datetime.now(timezone.utc),
                user=user
            )

            if cur_time.time() < time(hour=9, minute=0, second=0):
                remind.remind_first = True
                remind.remind_second = True
                remind.remind_weight = True
                if remind.day_without_indication_weight == 0:
                    remind.day_without_indication_weight = 1

                await remind.asave()
        except:
            ...


async def check_remind(cur_time, user):
    remind = await user.remind.alast()
    remind_first = remind.remind_first
    remind_second = remind.remind_second
    day_without_indication_weight = remind.day_without_indication_weight
    remind_weight = remind.remind_weight

    if (cur_time.time() > time(hour=12, minute=0, second=0)
        and cur_time.time() < time(hour=21, minute=0, second=0)
            and day_without_indication_weight == 0
            and remind_weight == True):
        return 'send_weight'

    if (cur_time.time() > time(hour=13, minute=0, second=0)
        and cur_time.time() < time(hour=21, minute=0, second=0)
            and remind_first == True):
        return 'send_first'

    if (cur_time.time() > time(hour=19, minute=0, second=0)
        and cur_time.time() < time(hour=21, minute=0, second=0)
        and remind_second == True
            and user.stage.last().stage == 5):
        return 'send_second'
