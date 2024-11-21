import telebot
import requests
import json
from telebot import types

TOKEN = '8105626795:AAF9fWmYsV1_1xYUlcWClkpiO-lXNl8wrfY' # Token Telegram бота
API = 'cc235ca7ba46ea82e1de3426aaeebb92' # API key від openweathermap

bot = telebot.TeleBot(TOKEN)

# API-ключ OpenWeatherMap
API_KEY = API

# URL OpenWeatherMap
BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'

# Обробник команди /start
@bot.message_handler(commands=['start'])
def start(message):
    # Створюємо кнопки для швидкого вибору міста
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    markup.add("Київ", "Львів", "Одеса", "Харків", "Чернівці")
    bot.send_message(
        message.chat.id,
        "Привіт! Натисни на одну з кнопок, щоб дізнатися погоду в цих містах, або введи назву іншого міста 🌤️",
        reply_markup=markup
    )

# Обробник текстових повідомлень
@bot.message_handler(content_types=['text'])
def get_weather(message):
    city = message.text.strip().lower()  # Отримуємо назву міста від користувача

    # Формуємо запит до OpenWeatherMap
    params = {
        'q': city,         # Назва міста
        'appid': API_KEY,  # API-ключ
        'units': 'metric', # Одиниці вимірювання (Цельсій)
        'lang': 'uk'       # Мова відповіді
    }

    res = requests.get(BASE_URL, params=params)  # Надсилаємо GET-запит

    if res.status_code == 200:  # Якщо запит успішний
        data = json.loads(res.text)  # Перетворюємо відповідь у JSON
        temp = data["main"]["temp"]  # Отримуємо температуру
        weather = data["weather"][0]["description"]  # Отримуємо опис погоди
        city_name = data["name"]  # Отримуємо назву міста

        # Надсилаємо користувачу повідомлення з погодою
        bot.reply_to(
            message,
            f"Погода в місті *{city_name}*:\n"
            f"🌡️ Температура: {temp}°C\n"
            f"☁️ Опис: {weather.capitalize()}",
            parse_mode='Markdown'
        )
    else:
        # Якщо місто не знайдено або сталася помилка
        bot.reply_to(message, "Місто вказано невірно. Перевірте назву та спробуйте ще раз.")

# Запуск бота
bot.polling(none_stop=True)
