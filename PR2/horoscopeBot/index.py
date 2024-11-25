import telebot
from telebot import types
import requests
from datetime import datetime
from deep_translator import GoogleTranslator

# Токен Telegram бота
TOKEN = '7710722442:AAFr0rW7G6uozZBhIAxduV60do-6_bDqkqM'

# API URL та ключ
HOROSCOPE_API_URL = "https://horoscope-app-api.vercel.app/api/v1/get-horoscope/daily"

# Ініціалізація бота
bot = telebot.TeleBot(TOKEN)

# Список знаків зодіаку українською мовою та їх відповідність англійським назвам
zodiac_signs_uk = [
    "Овен", "Телець", "Близнюки", "Рак", "Лев", "Діва",
    "Терези", "Скорпіон", "Стрілець", "Козоріг", "Водолій", "Риби"
]

zodiac_signs_map = {
    "Овен": "Aries",
    "Телець": "Taurus",
    "Близнюки": "Gemini",
    "Рак": "Cancer",
    "Лев": "Leo",
    "Діва": "Virgo",
    "Терези": "Libra",
    "Скорпіон": "Scorpio",
    "Стрілець": "Sagittarius",
    "Козоріг": "Capricorn",
    "Водолій": "Aquarius",
    "Риби": "Pisces"
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

        # Переходимо до вибору дати
        bot.send_message(
            message.chat.id,
            "Виберіть дату для гороскопу (формат: YYYY-MM-DD), або напишіть 'Сьогодні' для отримання гороскопу на сьогодні."
        )
        # Зберігаємо вибраний знак зодіаку для наступного кроку
        bot.register_next_step_handler(message, lambda m: request_horoscope(m, sign_en, sign_uk))
    else:
        bot.send_message(
            message.chat.id,
            "Будь ласка, оберіть знак зодіаку з меню або введіть його коректно."
        )

# Обробка введеної дати
def request_horoscope(message, sign_en, sign_uk):
    date_str = message.text.strip()
    if date_str.lower() == "сьогодні":
        date_str = datetime.today().strftime('%Y-%m-%d')
    else:
        try:
            # Перевіряємо, чи правильний формат дати
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            date_str = date_obj.strftime('%Y-%m-%d')
        except ValueError:
            bot.send_message(
                message.chat.id,
                "Невірний формат дати. Використовуйте формат YYYY-MM-DD."
            )
            return

    # Отримуємо гороскоп з API
    horoscope = get_horoscope(sign_en, date_str)
    if horoscope:
        # Перекладаємо гороскоп на українську
        horoscope_uk = translate_text(horoscope)
        bot.send_message(
            message.chat.id,
            f"Гороскоп для {sign_uk} на {date_str}:\n{horoscope_uk}"
        )
    else:
        bot.send_message(
            message.chat.id,
            "На жаль, не вдалося отримати гороскоп. Спробуйте пізніше."
        )

# Функція для отримання гороскопу через API
def get_horoscope(sign, date):
    try:
        # Формуємо запит до API
        response = requests.get(
            HOROSCOPE_API_URL,
            params={"sign": sign, "day": date}
        )
        if response.status_code == 200:
            data = response.json()
            # Перевіряємо, чи є гороскоп у відповіді
            return data.get('horoscope', data['data']['horoscope_data'])
        else:
            print(f"Помилка запиту: {response.status_code}")
            print(f"Деталі: {response.text}")
            return None
    except Exception as e:
        print(f"Помилка отримання гороскопу: {e}")
        return None
# Функція для перекладу тексту
def translate_text(text):
    try:
        # Переклад на українську
        translated = GoogleTranslator(source='en', target='uk').translate(text)
        return translated
    except Exception as e:
        print(f"Помилка перекладу: {e}")
        return text
# Запуск бота
bot.polling(none_stop=True)
