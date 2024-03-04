from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from dotenv import load_dotenv
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext


from model.models import *
from bot.SqlQueryAsync import *
from bot.SendMessageAsync import *
from bot.InlineKeyboardAsync import *
from bot.ButtonAsync import *
from bot.State import StateForm
from bot.config import TYPE

load_dotenv()
TOKEN = os.getenv('TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())


async def main():
    await dp.start_polling(bot)


class Command(BaseCommand):
    help = 'Запуск тг бота'

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
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(
                        text='Начать работу',
                        callback_data='login'
                    )
                ]])
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

        user_stage_guide.stage = 0
        await user_stage_guide.asave()

    @dp.message(StateForm.GET_AGE)
    async def get_age(message: types.Message, state: FSMContext):
        await change_info(message, 'age', state, bot)

    @dp.message(StateForm.GET_HEIGHT)
    async def get_age(message: types.Message, state: FSMContext):
        await change_info(message, 'height', state, bot)

    @dp.message(StateForm.GET_TARGET_WEIGHT)
    async def get_age(message: types.Message, state: FSMContext):
        await change_target_weight(message, 'target_weight', state, bot)

    @dp.message(StateForm.GET_CUR_WEIGHT)
    async def get_age(message: types.Message, state: FSMContext):
        await change_target_weight(message, 'cur_weight', state, bot)

    @dp.message()
    async def info(message: types.Message):
        try:
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

    def handle(self, *args, **options):
        print('start bot')
        asyncio.run(main())
