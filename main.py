import os
import requests
import json
from keyboards import *
from aiogram import Bot, Dispatcher, executor, types
from stickers_dict import sticker_dictionary

bot = Bot(token=os.environ["BOT_TOKEN"])
dp = Dispatcher(bot)

API_TOKEN = os.environ["API_TOKEN"]

headers = {'token': API_TOKEN}

balance_keyboard = BalanceKeyboard()


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Добро пожаловать в мир пчеловодства! Сейчас мы проверим, зарегистрирован ли ты")
    await check_register(message)


@dp.message_handler(commands=['help'])
async def send_commands(message):
    await bot.send_sticker(message.chat.id, sticker_dictionary['cool'],
                           reply_markup=MainCommandsKeyboard.keyboard)


@dp.callback_query_handler(lambda button: button.data)
async def process_callback_commands(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)

    message = callback_query.message

    if callback_query.data == 'main':
        await bot.edit_message_reply_markup(message.chat.id, message.message_id,
                                            reply_markup=MainCommandsKeyboard.keyboard)

    elif callback_query.data == 'balance':
        data = await get_request_api(message, table_name='user')
        if data:
            balance = data['balance']
            balance_keyboard.value = InlineKeyboardButton(balance, callback_data='empty')
            balance_keyboard.update()
            await bot.edit_message_reply_markup(message.chat.id, message.message_id,
                                                reply_markup=balance_keyboard.keyboard)


async def check_register(message: types.Message):
    response = await post_request_api(message)
    if response.status_code == 409:
        await bot.send_message(message.chat.id, "Вы уже зарегистрированы 🐝")
        await send_commands(message)
    elif response.status_code == 200:
        await bot.send_message(message.chat.id, 'Вы успешно зарегистрировались, приятного пользования!')
        await send_commands(message)
    elif response.status_code == 401:
        await bot.send_message(message.chat.id, "Неверный токен")
    else:
        await bot.send_message(message.chat.id,
                               "Непредвиденная ошибка, свяжитесь с разработчиком - ivan.galochkin0@gmail.com")


async def post_request_api(message):
    try:
        data = json.dumps({"telegram_id": message.from_user.id + 230})
        response = requests.post(f"http://127.0.0.1:8000/users", data=data, headers=headers)
        return response
    except ConnectionError:
        await bot.send_message(message.chat.id, "Технические работы на сервере")
        return 0


async def get_request_api(message, table_name):
    data = {"telegram_id": message.from_user.id,
            "table_name": table_name}
    try:
        response = requests.get(f"http://127.0.0.1:8000/users", params=data, headers=headers)
        return response.json()
    except requests.exceptions.ConnectionError:
        await bot.send_message(message.chat.id, "Технические работы на сервере")


executor.start_polling(dp)
