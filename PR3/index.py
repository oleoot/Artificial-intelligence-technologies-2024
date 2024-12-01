from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import F
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import asyncio
import random
import sqlite3

# Ініціалізація бота
TOKEN = '7923883606:AAH9We_31SgEgKfavvbyJ9CgO6gYYt8u1a0'
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Ініціалізація SQLite
conn = sqlite3.connect('repair_orders.db', check_same_thread=False)
cursor = conn.cursor()

# Створення таблиці, якщо вона не існує
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

# Функції роботи з базою даних
def add_order(order_id, name, phone, phone_model, problem_description, status):
    cursor.execute('''
    INSERT INTO orders (order_id, name, phone, phone_model, problem_description, status)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (order_id, name, phone, phone_model, problem_description, status))
    conn.commit()

def get_order_status(order_id):
    cursor.execute('SELECT * FROM orders WHERE order_id = ?', (order_id,))
    return cursor.fetchone()

# Головне меню
async def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.button(text="Категорії послуг")
    builder.button(text="Запис на ремонт")
    builder.button(text="Статус ремонту")
    builder.button(text="Про нас")
    builder.button(text="Контакти та розташування")
    return builder.as_markup(resize_keyboard=True)

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    menu = await main_menu()
    photo = types.FSInputFile("PR1/photos/1.jpg")
    welcome_text = (
        "Вітаємо вас у нашій майстерні з ремонту телефонів! 📱\n\n"
        "Ми спеціалізуємося на швидкому та якісному ремонті телефонів різних брендів і моделей. "
        "Наша команда складається з досвідчених майстрів, які використовують сучасні інструменти та високоякісні запчастини. "
        "Ми розуміємо, наскільки важливий ваш пристрій, тому докладаємо всіх зусиль для швидкого і надійного відновлення його працездатності.\n\n"
        "💼 Чому обирають нас?\n"
        "- Безкоштовна діагностика для визначення точної причини поломки\n"
        "- Гарантія на всі види ремонтних робіт\n"
        "- Прозора вартість послуг без прихованих платежів\n"
        "- Індивідуальний підхід до кожного клієнта\n\n"
        "Для початку виберіть потрібний розділ з меню нижче, і ми допоможемо вам повернути ваш пристрій до життя! 😊"
    )
    await message.answer_photo(photo=photo, caption=welcome_text, reply_markup=menu)

# Обробка текстових повідомлень
@dp.message(F("Категорії послуг"))
async def handle_categories(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Діагностика", callback_data="diagnostics")],
        [InlineKeyboardButton(text="Заміна екрана", callback_data="screen_replacement")],
        [InlineKeyboardButton(text="Заміна батареї", callback_data="battery_replacement")],
        [InlineKeyboardButton(text="Ремонт роз'єму зарядки", callback_data="charging_port_repair")],
        [InlineKeyboardButton(text="Інша поломка", callback_data="other_issue")]
    ])
    await message.answer("Оберіть категорію послуг:", reply_markup=keyboard)

@dp.message(F("Запис на ремонт"))
async def handle_book_repair(message: types.Message):
    await message.answer(
        "Будь ласка, надішліть наступну інформацію для запису:\n- Ваше ім'я\n- Номер телефону\n- Модель телефону\n- Опис проблеми"
    )

@dp.message(F("Статус ремонту"))
async def handle_status(message: types.Message):
    await message.answer("Введіть номер вашого замовлення для перевірки статусу.")

@dp.message(F("Про нас"))
async def handle_about(message: types.Message):
    photo = types.FSInputFile("PR1/photos/2.png")
    await message.answer_photo(
        photo=photo,
        caption=(
            "Ми - професійна майстерня з ремонту телефонів з багаторічним досвідом роботи. "
            "Пропонуємо швидкий та якісний ремонт різних моделей телефонів. "
            "Наша мета - зробити ваш пристрій знову як новий!"
        )
    )

@dp.message(F("Контакти та розташування"))
async def handle_contacts(message: types.Message):
    await message.answer(
        "Наша майстерня знаходиться за адресою: проспект Степана Бандери, 4, Київ.\n"
        "Графік роботи: Пн-Пт з 9:00 до 18:00.\nТелефон для довідок: +380123456789"
    )

# Callback обробка
@dp.callback_query(F.callback_data.in_({"diagnostics", "screen_replacement", "battery_replacement", "charging_port_repair", "other_issue"}))
async def callback_service_info(call: types.CallbackQuery):
    descriptions = {
        "diagnostics": "🔍 **Діагностика**\n\nДіагностика дозволяє точно визначити причину несправності вашого телефону.",
        "screen_replacement": "📱 **Заміна екрана**\n\nМи пропонуємо заміну екранів для більшості моделей телефонів.",
        "battery_replacement": "🔋 **Заміна батареї**\n\nШвидко розряджається телефон? Ми замінимо батарею на нову.",
        "charging_port_repair": "🔌 **Ремонт роз'єму зарядки**\n\nМи виправимо або замінимо роз'єм зарядки.",
        "other_issue": "📞 **Інша поломка**\n\nОпишіть проблему, і ми допоможемо знайти найкраще рішення."
    }
    description = descriptions[call.data]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Записатися", callback_data=f"register_{call.data}")]
    ])
    await call.message.answer(description, reply_markup=keyboard)

# Callback для запису
@dp.callback_query(F.callback_data.startswith("register_"))
async def callback_register(call: types.CallbackQuery):
    await call.message.answer(
        "Будь ласка, надішліть наступну інформацію для запису:\n- Ваше ім'я\n- Номер телефону\n- Модель телефону\n- Опис проблеми"
    )

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
