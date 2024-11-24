import telebot
from telebot import types
import requests

# Токен Telegram бота
TOKEN = '7710722442:AAFr0rW7G6uozZBhIAxduV60do-6_bDqkqM'

# API URL та ключ
HOROSCOPE_API_URL = "https://best-daily-astrology-and-horoscope-api.p.rapidapi.com/"
API_HEADERS = {
    "X-RapidAPI-Key": "724ed999b3mshff5d7606cc7d925p17919ajsnb4754afb0374",
    "X-RapidAPI-Host": "best-daily-astrology-and-horoscope-api.p.rapidapi.com"
}

# Ініціалізація бота
bot = telebot.TeleBot(TOKEN)

# Список знаків зодіаку українською мовою та їх відповідність англійським назвам
zodiac_signs_uk = [
    "Овен", "Телець", "Близнюки", "Рак", "Лев", "Діва",
    "Терези", "Скорпіон", "Стрілець", "Козоріг", "Водолій", "Риби"
]

zodiac_signs_map = {
    "Овен": "aries",
    "Телець": "taurus",
    "Близнюки": "gemini",
    "Рак": "cancer",
    "Лев": "leo",
    "Діва": "virgo",
    "Терези": "libra",
    "Скорпіон": "scorpio",
    "Стрілець": "sagittarius",
    "Козоріг": "capricorn",
    "Водолій": "aquarius",
    "Риби": "pisces"
}

# Обробник команди /start
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    markup.add(*zodiac_signs_uk)
    bot.send_message(
        message.chat.id,
        "Привіт! 👋 Я бот для отримання гороскопів 🌟.\n\n"
        "❓ Як я можу допомогти:\n"
        "- Оберіть свій знак зодіаку з меню нижче, щоб отримати гороскоп на сьогодні.\n\n"
        "💡 Якщо потрібна додаткова інформація, введіть команду /help.",
        reply_markup=markup
    )

# Обробник команди /help
@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(
        message.chat.id,
        "❓ Як користуватися ботом:\n\n"
        "1️⃣ Оберіть свій знак зодіаку з меню або введіть його назву.\n"
        "2️⃣ Отримайте гороскоп на сьогодні у форматі:\n"
        "   'Гороскоп для Овна на сьогодні: ...'\n\n"
        "💡 Підтримуються 12 знаків зодіаку:\n"
        "Овен, Телець, Близнюки, Рак, Лев, Діва, Терези, Скорпіон, Стрілець, Козоріг, Водолій, Риби."
    )

# Обробка текстових повідомлень
@bot.message_handler(content_types=['text'])
def handle_text(message):
    sign_uk = message.text.strip().capitalize()
    if sign_uk in zodiac_signs_map:
        # Отримуємо англійську назву знаку
        sign_en = zodiac_signs_map[sign_uk]
        horoscope = get_horoscope(sign_en)
        if horoscope:
            bot.send_message(
                message.chat.id,
                f"Гороскоп для {sign_uk} на сьогодні:\n{horoscope}"
            )
        else:
            bot.send_message(
                message.chat.id,
                "На жаль, не вдалося отримати гороскоп. Спробуйте пізніше."
            )
    else:
        bot.send_message(
            message.chat.id,
            "Будь ласка, оберіть знак зодіаку з меню або введіть його коректно."
        )

# Функція для отримання гороскопу через API
def get_horoscope(sign):
    try:
        response = requests.get(
            HOROSCOPE_API_URL,
            headers=API_HEADERS,
            params={"zodiacSign": sign}
        )
        if response.status_code == 200:
            data = response.json()
            return data.get('horoscope', "Гороскоп недоступний.")
        else:
            print(f"Помилка запиту: {response.status_code}")
            print(f"Деталі: {response.text}")
            return None
    except Exception as e:
        print(f"Помилка отримання гороскопу: {e}")
        return None

# Запуск бота
bot.polling(none_stop=True)
