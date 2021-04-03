from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class MainCommandsKeyboard:
    balance = InlineKeyboardButton("Баланс 💵", callback_data='balance')
    shop = InlineKeyboardButton("Магазин 🛒", callback_data='shop')

    keyboard = InlineKeyboardMarkup().add(balance, shop)


class BalanceKeyboard:
    value = InlineKeyboardButton("NOT FOUND", callback_data='empty')
    exit = InlineKeyboardButton("Назад", callback_data='main')
    keyboard = None

    def update(self):
        self.keyboard = InlineKeyboardMarkup().add(self.value, self.exit)
