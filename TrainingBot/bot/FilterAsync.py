from aiogram.filters import Filter

from bot.SqlQueryAsync import get_stage, get_user


class FilterGetCalories(Filter):
    def __init__(self, bot):
        self.bot = bot

    async def __call__(self, message):
        id = message.chat.id
        if id not in await get_user('id'):
            return False

        if await get_stage(id) in (4, 5):
            if message.text in ('Мои данные', 'Моя цель', 'Моя программа', 'Меню',
                                'Мастер обучения', 'Статистика за день',
                                'Статистика за неделю', 'Сброс', 'Мониторинг',
                                'Я все вспомнил'):
                return False
            if any([x in message.text for x in ['!', '^', ',', ';', ':', '#', '%', '?', r'\n']]):
                await self.bot.send_message(
                    chat_id=id,
                    text='Вводите согласно формату, повторите попытку',
                )
                return False
            return True
        return False
