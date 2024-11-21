import telebot
import requests
from datetime import datetime
from telebot import types
import sqlite3

TOKEN = '8105626795:AAF9fWmYsV1_1xYUlcWClkpiO-lXNl8wrfY' # Token Telegram бота
API = 'cc235ca7ba46ea82e1de3426aaeebb92' # API key від openweathermap

bot = telebot.TeleBot(TOKEN)

# API-ключ OpenWeatherMap
API_KEY = API

# URL OpenWeatherMap
BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'

# Підключення до бази даних SQLite
conn = sqlite3.connect('PR2/WeatherBot/weather_data.db', check_same_thread=False)
cursor = conn.cursor()

# Створення таблиці, якщо її ще немає
cursor.execute('''
CREATE TABLE IF NOT EXISTS weather (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT,
    date TEXT,
    temperature REAL,
    weather_description TEXT,
    wind_speed REAL
)
''')
conn.commit()

# Функція для збереження даних у базу
def save_weather_to_db(city, date, temperature, weather_description, wind_speed):
    cursor.execute('''
        INSERT INTO weather (city, date, temperature, weather_description, wind_speed)
        VALUES (?, ?, ?, ?, ?)
    ''', (city, date, temperature, weather_description, wind_speed))
    conn.commit()

# Створюємо кнопки для швидкого вибору міста
def create_reply_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    markup.add("Київ", "Львів", "Одеса", "Харків", "Чернівці")
    return markup
# Обробник команди /start
@bot.message_handler(commands=['start'])
def start(message):
    markup = create_reply_markup()
    bot.send_message(
        message.chat.id,
        "Привіт! 👋 Я бот для отримання актуальної погоди 🌤️.\n\n"
        "❓ Як мене використовувати:\n"
        "- Надішли мені назву міста або натисни кнопку швидкого вибору і я розповім про поточну погоду в ньому.\n\n"
        "💡 Наприклад:\n"
        "- Київ\n"
        "- Львів\n"
        "- Одеса\n\n"
        "Щоб отримати детальнішу інформацію про функції, введи команду /help.",
        reply_markup=markup
    )

# Обробник команди /help
@bot.message_handler(commands=['help'])
def help_command(message):
    markup = create_reply_markup()
    bot.send_message(
        message.chat.id,
        "❓ Допомога по боту:\n\n"
        "Цей бот дозволяє швидко дізнатися актуальну погоду в будь-якому місті світу.\n"
        "Просто надішли назву міста українською чи англійською, і я надішлю тобі:\n"
        "- Назву міста та поточну дату\n"
        "- Температуру в градусах Цельсія 🌡️\n"
        "- Опис погоди ☁️\n"
        "- Швидкість вітру 💨\n\n"
        "📌 Приклад використання:\n"
        "- Надішли: Київ\n"
        "- Отримай інформацію про погоду в Києві.\n\n"
        "Якщо щось не працює, перевір правильність назви міста або спробуй ще раз!",
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
        data = res.json()  # Перетворюємо відповідь у JSON
        city_name = data['name']  # Назва міста
        temp = data['main']['temp']  # Температура
        weather = data['weather'][0]['description'].capitalize()  # Опис погоди
        wind_speed = data['wind']['speed']  # Швидкість вітру
        current_date = datetime.now().strftime('%d-%m-%Y')  # Поточна дата

        # Зберігаємо дані у базу
        save_weather_to_db(city_name, current_date, temp, weather, wind_speed)

        # Формуємо відформатовану відповідь
        response = (
            f"Погода в {city_name} на {current_date}:\n"
            f"🌡️ Температура: {temp}°C\n"
            f"☁️ Опис: {weather}\n"
            f"💨 Швидкість вітру: {wind_speed} м/с"
        )
        markup = create_reply_markup()
        bot.send_message(message.chat.id, response, reply_markup=markup)
    else:
        # Якщо місто не знайдено або сталася помилка
        bot.reply_to(message, "Місто вказано невірно. Перевірте назву та спробуйте ще раз.")

# Запуск бота
bot.polling(none_stop=True)
