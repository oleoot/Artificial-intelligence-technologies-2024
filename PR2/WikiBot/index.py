import telebot
import wikipediaapi

# Ініціалізація бота
bot = telebot.TeleBot('7601619889:AAFBCQrwMxacsnrDiaG-LqehyxJ_Qvrd8Y8')

# Ініціалізація Wikipedia API
wiki = wikipediaapi.Wikipedia(
    language='uk',
    user_agent='MyTelegramBot/1.0 (https://meta.wikimedia.org/wiki/User-Agent_policy)'
)

# Обробник команди /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Привіт! Надішли мені текст, і я знайду відповідну статтю у Вікіпедії 📖\n"
        "Формат відповіді буде:\n"
        "1. Назва статті\n"
        "2. Основний текст\n"
        "3. Посилання на статтю"
    )

# Обробник текстових повідомлень
@bot.message_handler(content_types=['text'])
def search_wikipedia(message):
    query = message.text.strip()  # Отримуємо запит від користувача

    # Шукаємо статтю у Вікіпедії
    page = wiki.page(query)

    if page.exists():  # Якщо стаття знайдена
        # Отримуємо основний текст (перші 500 символів)
        summary = page.summary[:500] + "..." if len(page.summary) > 500 else page.summary
        # Формуємо відповідь
        response = (
            f"1. Назва статті: {page.title}\n\n"
            f"2. Основний текст:\n{summary}\n\n"
            f"3. Посилання на статтю: {page.fullurl}"
        )
        bot.send_message(message.chat.id, response)
    else:
        # Якщо стаття не знайдена
        bot.send_message(
            message.chat.id,
            "На жаль, я не зміг знайти відповідну статтю. Спробуйте уточнити запит."
        )

# Запуск бота
bot.polling(none_stop=True)
