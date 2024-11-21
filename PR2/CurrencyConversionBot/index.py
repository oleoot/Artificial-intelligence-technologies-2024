import telebot
import requests
from telebot import types
import sqlite3

TOKEN = '7613696382:AAHBxmYz0iXrbYSUGvCRJiBhbEF4XKaLQWk' # Token Telegram бота
API = '279718da18519c937c69ae2b' # API key від exchangerate

# Ініціалізація бота
bot = telebot.TeleBot(TOKEN)

# API-ключ для ExchangeRate API
API_KEY = API
BASE_URL = f'https://v6.exchangerate-api.com/v6/{API_KEY}/latest/'

# Підключення до бази даних SQLite
conn = sqlite3.connect('PR2/CurrencyConversionBot/currency_conversion.db', check_same_thread=False)
cursor = conn.cursor()

# Створення таблиці, якщо її ще немає
cursor.execute('''
CREATE TABLE IF NOT EXISTS conversions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    amount REAL,
    base_currency TEXT,
    target_currency TEXT,
    converted_amount REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')
conn.commit()

# Функція для збереження запиту конвертації у базу даних
def save_conversion_to_db(user_id, username, amount, base_currency, target_currency, converted_amount):
    cursor.execute('''
        INSERT INTO conversions (user_id, username, amount, base_currency, target_currency, converted_amount)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, username, amount, base_currency, target_currency, converted_amount))
    conn.commit()

# Обробник команди /start
@bot.message_handler(commands=['start'])
def start(message):
    # Клавіатура для вибору дій
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    markup.add("Конвертувати валюту", "Курси валют", "Допомога")
    bot.send_message(
        message.chat.id,
        "Привіт! 👋 Я допоможу тобі з конвертацією валют 💱.\n\n"
        "❓ Як користуватися ботом:\n"
        "- Натисни 'Конвертувати валюту', щоб розрахувати обмін між двома валютами.\n"
        "- Натисни 'Курси валют', щоб переглянути поточні курси валют.\n"
        "- Натисни 'Допомога', щоб отримати додаткову інформацію.\n\n"
        "💡 Надішли запит у форматі:\n"
        "<сума> <базова валюта> в <цільова валюта>\n"
        "Наприклад: 100 USD в EUR\n\n"
        "Оберіть дію з меню нижче:",
        reply_markup=markup
    )

# Обробник команди /help
@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(
        message.chat.id,
        "❓ Допомога по боту:\n\n"
        "Цей бот дозволяє:\n"
        "- Конвертувати валюти. Для цього введіть запит у форматі:\n"
        "  <сума> <базова валюта> в <цільова валюта>\n"
        "  Наприклад: 100 USD в EUR\n\n"
        "- Переглядати поточні курси валют. Для цього введіть команду /rates або виберіть 'Курси валют'.\n\n"
        "💡 Валюти потрібно вводити у форматі ISO-кодів (наприклад, USD, EUR, UAH)."
    )

# Обробник команди /rates
@bot.message_handler(commands=['rates'])
def rates_command(message):
    response = requests.get(BASE_URL + 'USD')  # Отримання курсів щодо USD
    if response.status_code == 200:
        data = response.json()
        rates = data.get('conversion_rates', {})
        # Вибираємо основні валюти
        currencies = ['USD', 'EUR', 'UAH', 'GBP', 'JPY']
        rates_list = "\n".join([f"{currency}: {rates[currency]}" for currency in currencies if currency in rates])
        bot.send_message(
            message.chat.id,
            f"💱 Поточні курси валют щодо USD:\n{rates_list}"
        )
    else:
        bot.send_message(
            message.chat.id,
            "Не вдалося отримати курси валют. Спробуйте пізніше."
        )

# Обробник текстових повідомлень
@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text == "Конвертувати валюту":
        bot.send_message(message.chat.id, "Введіть запит у форматі:\n<сума> <базова валюта> в <цільова валюта>\nНаприклад: 100 USD в EUR")
    elif message.text == "Курси валют":
        rates_command(message)  # Викликаємо команду /rates
    elif message.text == "Допомога":
        help_command(message)  # Викликаємо команду /help
    else:
        process_conversion(message)

# Конвертація валют
def process_conversion(message):
    try:
        # Очікується формат: <сума> <базова валюта> в <цільова валюта>
        parts = message.text.split()
        if len(parts) != 4 or parts[2].lower() != "в":
            raise ValueError("Неправильний формат запиту")

        amount = float(parts[0])  # Сума
        base_currency = parts[1].upper()  # Базова валюта
        target_currency = parts[3].upper()  # Цільова валюта

        # Отримання курсів для базової валюти
        response = requests.get(BASE_URL + base_currency)
        if response.status_code == 200:
            data = response.json()
            rate = data['conversion_rates'].get(target_currency)
            if rate:
                converted_amount = amount * rate
                save_conversion_to_db(
                    message.from_user.id,
                    message.from_user.username,
                    amount,
                    base_currency,
                    target_currency,
                    converted_amount
                )
                bot.send_message(
                    message.chat.id,
                    f"{amount} {base_currency} = {converted_amount:.2f} {target_currency}"
                )
            else:
                bot.send_message(message.chat.id, f"Не вдалося знайти курс для {target_currency}.")
        else:
            bot.send_message(message.chat.id, "Не вдалося отримати дані. Перевірте код валюти.")
    except Exception:
        bot.send_message(
            message.chat.id,
            "Будь ласка, введіть запит у правильному форматі:\n<сума> <базова валюта> в <цільова валюта>"
        )

# Запуск бота
bot.polling(none_stop=True)
