from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Каталог")],
            [KeyboardButton(text="Інформація"), KeyboardButton(text="Допомога")]
        ],
        resize_keyboard=True
    )
def main_menu_reply():
    """
    Генерує головне меню для відображення під рядком вводу.
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Каталог")],
            [KeyboardButton(text="Кошик 🛒")],
            [KeyboardButton(text="Інформація"), KeyboardButton(text="Допомога")]
        ],
        resize_keyboard=True  # Зменшує клавіатуру під розмір кнопок
    )
