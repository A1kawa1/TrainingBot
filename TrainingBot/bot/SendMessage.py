from datetime import time
from model.models import Message
from bot.InlineKeyboard import create_keyboard_stage, last_message


def template_send_message(bot, chat_id, key):
    messages = Message.objects.filter(mesKey=key).order_by('order')
    if '_last' in key:
        bot.send_message(
            chat_id=chat_id,
            text=messages[0].message,
            reply_markup=last_message(key)
        )
    else:
        for mes in messages:
            bot.send_message(
                chat_id=chat_id,
                text=mes.message,
                reply_markup=create_keyboard_stage(chat_id)
            )


def check_remind(cur_time, user):
    remind_first = user.remind.last().remind_first
    remind_second = user.remind.last().remind_second
    if (cur_time.time() > time(hour=15, minute=0, second=0)
        and cur_time.time() < time(hour=21, minute=0, second=0)
            and remind_first == True):
        return 'send_first'
    if (cur_time.time() > time(hour=19, minute=0, second=0)
        and cur_time.time() < time(hour=21, minute=0, second=0)
        and remind_second == True
            and user.stage.last().stage == 5):
        return 'send_second'
