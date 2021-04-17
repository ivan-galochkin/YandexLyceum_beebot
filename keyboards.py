from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class MainCommandsKeyboard:
    balance = InlineKeyboardButton("Баланс 💵", callback_data='balance')
    shop = InlineKeyboardButton("Магазин 🛒", callback_data='shop')
    market = InlineKeyboardButton("Рынок", callback_data='market')
    keyboard = InlineKeyboardMarkup(row_width=2).add(balance, shop, market)

    def update(self):
        self.keyboard = InlineKeyboardMarkup(row_width=2).add(self.balance, self.shop, self.market)


class BalanceKeyboard:
    value = InlineKeyboardButton("NOT FOUND", callback_data='empty')
    exit = InlineKeyboardButton("Назад", callback_data='main')
    keyboard = InlineKeyboardMarkup().add(value, exit)

    def update(self):
        self.keyboard = InlineKeyboardMarkup().add(self.value, self.exit)


class MarketKeyboard:
    honey_count = InlineKeyboardButton("NOT FOUND", callback_data='empty')
    exit = InlineKeyboardButton("Назад", callback_data='main')
    keyboard = InlineKeyboardMarkup(row_width=1).add(honey_count, exit)

    def update(self):
        self.keyboard = InlineKeyboardMarkup(row_width=1).add(self.honey_count, self.exit)
