from datetime import datetime, timezone, timedelta, time
from time import sleep
from model.models import Message, User
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
