import os
import requests
import json
from keyboards import *
from aiogram import Bot, Dispatcher, executor, types
from stickers_dict import sticker_dictionary
import asyncio

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


async def keyboard_controller(callback_query):
    await bot.answer_callback_query(callback_query.id)
    if callback_query.data == 'main':
        keyboard = MainCommandsKeyboard()
    elif callback_query.data == 'balance':
        data = await get_request_api(callback_query.message, table_name='user')

        rounded_cash = round(data['balance'])

        keyboard = BalanceKeyboard()

        keyboard.value = InlineKeyboardButton(f"{rounded_cash} ₽", callback_data='balance')

    elif callback_query.data == "market":
        await put_request_api(callback_query.message, "unstable")
        data = await get_request_api(callback_query.message, table_name='honey')

        keyboard = MarketKeyboard()

        rounded_honey = round(data['honey'], 3)

        keyboard.honey_count = InlineKeyboardButton(f"Накоплено мёда: {rounded_honey}", callback_data='sell_honey')
    elif callback_query.data == "sell_honey":
        await put_request_api(callback_query.message, mode='sell')

        keyboard = MarketKeyboard()

        keyboard.honey_count = InlineKeyboardButton(f"Продано! Кликните для обновления!", callback_data="market")
    elif callback_query.data == "shop":
        keyboard = await get_shop_data(callback_query.message)
    elif "buy" in callback_query.data:
        keyboard = await buy_process(callback_query)

    if not keyboard:
        raise EmptyKeyboardError
    keyboard.update()

    return keyboard, callback_query.message


async def buy_process(callback_query):
    item = callback_query.data[4:]
    if "beehives" in item:
        table = "beehives"
        count = 1
    else:
        table = "bees"
        count = 100
    response = await put_request_api(callback_query.message, table, item, count, mode='buy')

    keyboard = await get_shop_data(callback_query.message)

    if response == "Not enough cash":
        if "beehives" in item:
            keyboard.beehives_count = InlineKeyboardButton("Недостаточно денег", callback_data="shop")
        else:
            keyboard.bees_count = InlineKeyboardButton("Недостаточно денег", callback_data="shop")
    elif response == "Not enough storage":
        keyboard.bees_count = InlineKeyboardButton("Постройте больше ульев", callback_data="shop")

    return keyboard


async def get_shop_data(message):
    bees = await get_request_api(message, "bees")
    beehives = await get_request_api(message, "beehives")
    keyboard = ShopKeyboard()

    keyboard.bees_count = InlineKeyboardButton(bees['regular_bees'], callback_data="buy_regular_bees")
    keyboard.beehives_count = InlineKeyboardButton(beehives['small_beehives'],
                                                   callback_data="buy_small_beehives")
    return keyboard


@dp.callback_query_handler(lambda button: button.data)
async def process_callback_commands(callback_query: types.CallbackQuery):
    try:
        keyboard, message = await keyboard_controller(callback_query)
        await bot.edit_message_reply_markup(message.chat.id, message.message_id,
                                            reply_markup=keyboard.keyboard)
    except EmptyKeyboardError:
        pass


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
        data = json.dumps({"telegram_id": message.from_user.id})
        response = requests.post(f"http://127.0.0.1:8000/users", data=data, headers=headers)
        return response
    except ConnectionError:
        await bot.send_message(message.chat.id, "Технические работы на сервере")
        return 0


async def get_request_api(message, table_name):
    data = {"telegram_id": message.chat.id,
            "table_name": table_name}
    try:
        response = requests.get(f"http://127.0.0.1:8000/users", params=data, headers=headers)
        return response.json()
    except requests.exceptions.ConnectionError:
        raise ServerDownError


async def put_request_api(message, table_name='empty', item='empty', count=0, mode="update"):
    data = {"telegram_id": message.chat.id,
            "table_name": table_name,
            "item": item,
            "count": count,
            "mode": mode
            }
    try:
        response = requests.put("http://127.0.0.1:8000/users", params=data, headers=headers)
        return response.json()
    except requests.exceptions.ConnectionError:
        raise ServerDownError


class ServerDownError(BaseException):
    pass


class EmptyKeyboardError(BaseException):
    pass


executor.start_polling(dp)
