from datetime import time

from model.models import Message
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
            except:
                ...


def check_remind(cur_time, user):
    remind = user.remind.last()
    remind_first = remind.remind_first
    remind_second = remind.remind_second
    day_without_indication_weight = remind.day_without_indication_weight
    remind_weight = remind.remind_weight
    if (cur_time.time() > time(hour=12, minute=0, second=0)
        and cur_time.time() < time(hour=21, minute=0, second=0)
            and day_without_indication_weight == 0
            and remind_weight == True):
        return 'send_weight'
    if (cur_time.time() > time(hour=15, minute=0, second=0)
        and cur_time.time() < time(hour=21, minute=0, second=0)
            and remind_first == True):
        return 'send_first'
    if (cur_time.time() > time(hour=19, minute=0, second=0)
        and cur_time.time() < time(hour=21, minute=0, second=0)
        and remind_second == True
            and user.stage.last().stage == 5):
        return 'send_second'
