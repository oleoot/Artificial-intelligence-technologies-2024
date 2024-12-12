from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, InputFile
import asyncio
import random
import sqlite3
import logging

# Логування
logging.basicConfig(level=logging.INFO)

# Token для прив'язки до телеграм бота
TOKEN = '7923883606:AAH9We_31SgEgKfavvbyJ9CgO6gYYt8u1a0'
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Ініціалізація SQLite
conn = sqlite3.connect('PR3/repair_orders.db', check_same_thread=False)
cursor = conn.cursor()

# Створення таблиці для збереження даних, якщо такої ще немає
cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    name TEXT,
    phone TEXT,
    phone_model TEXT,
    problem_description TEXT,
    status TEXT
)
''')
conn.commit()

# Контейнер для збереження контексту
user_context = {}

# Функція для додавання запису в базу даних
def add_order(order_id, name, phone, phone_model, problem_description, status):
    cursor.execute('''
    INSERT INTO orders (order_id, name, phone, phone_model, problem_description, status)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (order_id, name, phone, phone_model, problem_description, status))
    conn.commit()

# Функція для отримання статусу замовлення
def get_order_status(order_id):
    cursor.execute('SELECT * FROM orders WHERE order_id = ?', (order_id,))
    return cursor.fetchone()

# Обробник команди /start
async def start(message: types.Message):
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Категорії послуг"), types.KeyboardButton(text="Запис на ремонт")],
            [types.KeyboardButton(text="Статус ремонту"), types.KeyboardButton(text="Про нас")],
            [types.KeyboardButton(text="Контакти та розташування")]
        ],
        resize_keyboard=True
    )
    welcome_text = (
        "Вітаємо вас у нашій майстерні з ремонту телефонів! 📱\n\n"
        "Ми спеціалізуємося на швидкому та якісному ремонті телефонів різних брендів і моделей."
        "\n\n💼 Чому обирають нас?\n"
        "- Безкоштовна діагностика\n"
        "- Гарантія на всі види робіт\n"
        "- Прозора вартість послуг\n"
        "- Індивідуальний підхід\n"
        "\nОберіть потрібний розділ з меню нижче. 😊"
    )
    await message.answer(welcome_text, reply_markup=markup)

# Обробник текстових повідомлень
async def handle_text(message: types.Message):
    if message.text == "Категорії послуг":
        await get_categories(message)
    elif message.text == "Запис на ремонт":
        await request_user_info(message)
    elif message.text == "Статус ремонту":
        await get_status(message)
    elif message.text == "Про нас":
        await get_about(message)
    elif message.text == "Контакти та розташування":
        await get_contacts(message)
    elif message.text == "Назад":
        await main_menu(message)

# Повернення до головного меню
async def main_menu(message):
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Категорії послуг"), types.KeyboardButton(text="Запис на ремонт")],
            [types.KeyboardButton(text="Статус ремонту"), types.KeyboardButton(text="Про нас")],
            [types.KeyboardButton(text="Контакти та розташування")]
        ],
        resize_keyboard=True
    )
    await message.answer("Повертаємось до головного меню:", reply_markup=markup)

# Категорії послуг
async def get_categories(message):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Діагностика", callback_data='diagnostics')],
            [InlineKeyboardButton(text="Заміна екрана", callback_data='screen_replacement')],
            [InlineKeyboardButton(text="Заміна батареї", callback_data='battery_replacement')],
            [InlineKeyboardButton(text="Ремонт роз'єму зарядки", callback_data='charging_port_repair')],
            [InlineKeyboardButton(text="Інша поломка", callback_data='other_issue')]
        ]
    )
    await message.answer("Оберіть категорію послуг:", reply_markup=markup)

# Обробка натискання кнопок
async def callback_handler(call: types.CallbackQuery):
    if call.data in ['diagnostics', 'screen_replacement', 'battery_replacement', 'charging_port_repair', 'other_issue']:
        await category_info(call)
    elif call.data.startswith('register_'):
        await request_user_info(call.message, call.data)

# Інформація по вибраній категорії
async def category_info(call):
    descriptions = {
        'diagnostics': "🔍 **Діагностика**\n\nДозволяє точно визначити причину несправності.",
        'screen_replacement': "📱 **Заміна екрана**\n\nТривалість: 1-3 години.",
        'battery_replacement': "🔋 **Заміна батареї**\n\nТривалість: до 1 години.",
        'charging_port_repair': "🔌 **Ремонт роз'єму зарядки**\n\nВідновлення працездатності пристрою.",
        'other_issue': "📞 **Інша поломка**\n\nОпишіть проблему."
    }
    description = descriptions.get(call.data, "Категорія не знайдена")
    markup = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Записатися", callback_data=f'register_{call.data}')]]
    )
    await call.message.answer(description, parse_mode="Markdown", reply_markup=markup)

# Запит даних користувача для запису
async def request_user_info(message, category=None):
    user_context[message.chat.id] = {"action": "register"}
    if category:
        user_context[message.chat.id]["category"] = category.replace('register_', '').replace('_', ' ').capitalize()
    markup = ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="Назад")]],
        resize_keyboard=True
    )
    await message.answer(
        "Будь ласка, надішліть наступну інформацію у форматі:\nВаше ім'я, Номер телефону, Модель телефону",
        reply_markup=markup
    )
# Обробка текстових повідомлень
async def process_message(message: types.Message):
    context = user_context.get(message.chat.id, {})
    action = context.get("action")

    if action == "register":
        await process_user_info(message)
    elif action == "check_status":
        await process_order_status(message)
    else:
        await message.answer("Будь ласка, оберіть дію з меню.")

# Обробка введення даних користувача
async def process_user_info(message: types.Message):
    try:
        user_data = message.text.split(",")
        name = user_data[0].strip()
        phone = user_data[1].strip()
        phone_model = user_data[2].strip()
        context = user_context.get(message.chat.id, {})
        problem_description = context.get("category", "")
        order_id = str(random.randint(10000, 99999))
        status = "Замовлення підтверджено."

        add_order(order_id, name, phone, phone_model, problem_description, status)
        await message.answer(f"Дякуємо! Ваше замовлення підтверджено. Номер замовлення: {order_id}")
        await main_menu(message)
    except Exception as e:
        await message.answer("Будь ласка, введіть коректні дані у форматі: Ім'я, Телефон, Модель")

# Статус замовлення
async def get_status(message):
    user_context[message.chat.id] = {"action": "check_status"}
    await message.answer("Введіть номер вашого замовлення:")

# Обробка введення номера замовлення
async def process_order_status(message: types.Message):
    order_id = message.text.strip()
    order_info = get_order_status(order_id)
    if order_info:
        response = (
            f"Номер замовлення: {order_info[0]}\n"
            f"Ім'я: {order_info[1]}\n"
            f"Телефон: {order_info[2]}\n"
            f"Модель телефону: {order_info[3]}\n"
            f"Опис проблеми: {order_info[4]}\n"
            f"Статус: {order_info[5]}"
        )
    else:
        response = "Замовлення з таким номером не знайдено. Перевірте номер і спробуйте ще раз."
    await message.answer(response)
    await main_menu(message)

# Інформація про майстерню
async def get_about(message):
    markup = ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="Назад")]],
        resize_keyboard=True
    )
    await message.answer(
        "Ми - професійна майстерня з ремонту телефонів з багаторічним досвідом роботи. "
        "Пропонуємо швидкий та якісний ремонт різних моделей телефонів. "
        "Наша мета - зробити ваш пристрій знову як новий!",
        reply_markup=markup
    )

# Інформація про контакти
async def get_contacts(message):
    markup = ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="Назад")]],
        resize_keyboard=True
    )
    await message.answer(
        "Адреса: проспект Степана Бандери, 4, Київ.\n"
        "Графік роботи: Пн-Пт з 9:00 до 18:00.\n"
        "Телефон для довідок: +380123456789",
        reply_markup=markup
    )


# Реєстрація хендлерів
dp.message.register(start, F.text == "/start")
dp.message.register(handle_text, F.text.in_(["Категорії послуг", "Запис на ремонт", "Статус ремонту", "Про нас", "Контакти та розташування", "Назад"]))
# Реєстрація обробника текстових повідомлень
dp.message.register(process_message)
dp.callback_query.register(callback_handler)

# Активація бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
