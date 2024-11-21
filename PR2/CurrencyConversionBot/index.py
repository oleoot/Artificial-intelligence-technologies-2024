import telebot
import requests
from telebot import types

TOKEN = '7613696382:AAHBxmYz0iXrbYSUGvCRJiBhbEF4XKaLQWk' # Token Telegram бота
API = '279718da18519c937c69ae2b' # API key від openweathermap

# Ініціалізація бота
bot = telebot.TeleBot(TOKEN)

# API-ключ для ExchangeRate API
API_KEY = API
BASE_URL = f'https://v6.exchangerate-api.com/v6/{API_KEY}/latest/'

# Обробник команди /start
@bot.message_handler(commands=['start'])
def start(message):
    # Клавіатура для вибору дій
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    markup.add("Конвертувати валюту", "Курси валют", "Допомога")
    bot.send_message(
        message.chat.id,
        "Привіт! Я допоможу тобі з конвертацією валют 💱\n"
        "Оберіть дію з меню нижче:",
        reply_markup=markup
    )

# Обробник текстових повідомлень
@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text == "Конвертувати валюту":
        bot.send_message(message.chat.id, "Введіть запит у форматі:\n<сума> <базова валюта> в <цільова валюта>\nНаприклад: 100 USD в EUR")
    elif message.text == "Курси валют":
        bot.send_message(message.chat.id, "Введіть код базової валюти (наприклад, USD):")
        bot.register_next_step_handler(message, get_exchange_rates)
    elif message.text == "Допомога":
        bot.send_message(message.chat.id, "Я допоможу конвертувати валюти та показати їхні курси. Використовуйте меню для вибору дій.")
    else:
        process_conversion(message)

# Отримання курсів валют для базової валюти
def get_exchange_rates(message):
    base_currency = message.text.upper().strip()
    response = requests.get(BASE_URL + base_currency)
    if response.status_code == 200:
        data = response.json()
        rates = data.get('conversion_rates', {})
        rates_list = "\n".join([f"{currency}: {rate}" for currency, rate in rates.items()])
        bot.send_message(
            message.chat.id,
            f"Курси валют для {base_currency}:\n{rates_list}"
        )
    else:
        bot.send_message(message.chat.id, "Не вдалося отримати курси валют. Перевірте код валюти та спробуйте ще раз.")

# Конвертація валют
def process_conversion(message):
    try:
        # Очікується формат: <сума> <базова валюта> в <цільова валюта>
        parts = message.text.split()
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
                bot.send_message(
                    message.chat.id,
                    f"{amount} {base_currency} = {converted_amount:.2f} {target_currency}"
                )
            else:
                bot.send_message(message.chat.id, f"Не вдалося знайти курс для {target_currency}.")
        else:
            bot.send_message(message.chat.id, "Не вдалося отримати дані. Перевірте код валюти.")
    except Exception as e:
        bot.send_message(message.chat.id, "Будь ласка, введіть запит у правильному форматі:\n<сума> <базова валюта> в <цільова валюта>")

# Запуск бота
bot.polling(none_stop=True)
