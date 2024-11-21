import telebot
from telebot import types
import random

TOKEN = '7923883606:AAH9We_31SgEgKfavvbyJ9CgO6gYYt8u1a0'
bot = telebot.TeleBot(TOKEN)

order_status_db = {
    # "12345": "Ремонт завершено. Пристрій готовий до видачі.",
    # "67890": "Пристрій у процесі ремонту. Звертайтесь за оновленням через 2 дні.",
    # "54321": "Очікування запчастин. Ми зв'яжемось, як тільки ремонт буде відновлено."
}

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Категорії послуг", "Запис на ремонт", "Статус ремонту", "Про нас", "Контакти та розташування")
    bot.send_photo(message.chat.id, photo=open('./photos/1.jpg', 'rb'))
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

    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.message_handler(commands=['book'])
def book(message):
    request_user_info(message)

@bot.message_handler(commands=['status'])
def status(message):
    get_status(message)

@bot.message_handler(commands=['categories'])
def categories(message):
    get_categories(message)

@bot.message_handler(commands=['about'])
def about(message):
    get_about(message)

@bot.message_handler(commands=['contacts'])
def contacts(message):
    get_contacts(message)

@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text == "Про нас":
        get_about(message)
    elif message.text == "Категорії послуг":
        get_categories(message)

    elif message.text == "Діагностика":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Записатися", callback_data='register_diagnostics'))
        bot.send_message(
            message.chat.id,
            "🔍 **Діагностика**\n\n"
            "Діагностика дозволяє точно визначити причину несправності вашого телефону. "
            "Наші фахівці швидко проведуть огляд пристрою та запропонують найкращий варіант вирішення проблеми.",
            reply_markup=markup,
            parse_mode="Markdown"
        )

    elif message.text == "Заміна екрана":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Записатися", callback_data='register_screen_replacement'))
        bot.send_message(
            message.chat.id,
            "📱 **Заміна екрана**\n\n"
            "Ми пропонуємо заміну екранів для більшості моделей телефонів, використовуючи тільки якісні запчастини. "
            "Процедура займає від 1 до 3 годин залежно від моделі.",
            reply_markup=markup,
            parse_mode="Markdown"
        )

    elif message.text == "Заміна батареї":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Записатися", callback_data='register_battery_replacement'))
        bot.send_message(
            message.chat.id,
            "🔋 **Заміна батареї**\n\n"
            "Швидко розряджається телефон? Ми замінимо батарею на нову, щоб ваш пристрій працював довше. "
            "Тривалість заміни - до 1 години.",
            reply_markup=markup,
            parse_mode="Markdown"
        )

    elif message.text == "Ремонт роз'єму зарядки":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Записатися", callback_data='register_charging_port_repair'))
        bot.send_message(
            message.chat.id,
            "🔌 **Ремонт роз'єму зарядки**\n\n"
            "Ваш телефон не заряджається належним чином? Ми виправимо або замінимо роз'єм зарядки, "
            "щоб ваш пристрій працював як новий.",
            reply_markup=markup,
            parse_mode="Markdown"
        )

    elif message.text == "Інша поломка":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Записатися", callback_data='register_other_issue'))
        bot.send_message(
            message.chat.id,
            "📞 **Інша поломка**\n\n"
            "Якщо у вас інша проблема з телефоном, надішліть нам опис, і ми допоможемо знайти найкраще рішення.",
            reply_markup=markup,
            parse_mode="Markdown"
        )

    elif message.text == "Запис на ремонт":
        request_user_info(message)

    elif message.text == "Контакти та розташування":
        get_contacts(message)

    elif message.text == "Статус ремонту":
        get_status(message)

    elif message.text == "Назад":
        main_menu(message)

    elif message.text.isdigit():
        order_info = order_status_db.get(message.text)
        if order_info:
            response = f"Статус вашого замовлення: {order_info['status']}"
        else:
            response = "Замовлення з таким номером не знайдено. Перевірте номер і спробуйте ще раз."

        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, "Оберіть розділ з меню.")
def main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Категорії послуг", "Запис на ремонт", "Статус ремонту", "Про нас", "Контакти та розташування")
    bot.send_message(
        message.chat.id,
        "Повертаємось до головного меню. Оберіть розділ для продовження:",
        reply_markup=markup
    )
@bot.callback_query_handler(func=lambda call: call.data in ['diagnostics', 'screen_replacement', 'battery_replacement', 'charging_port_repair', 'other_issue'])
def category_info(call):
    if call.data == 'diagnostics':
        description = "🔍 **Діагностика**\n\nДіагностика дозволяє точно визначити причину несправності вашого телефону. Наші фахівці швидко проведуть огляд пристрою та запропонують найкращий варіант вирішення проблеми."
    elif call.data == 'screen_replacement':
        description = "📱 **Заміна екрана**\n\nМи пропонуємо заміну екранів для більшості моделей телефонів, використовуючи тільки якісні запчастини. Процедура займає від 1 до 3 годин залежно від моделі."
    elif call.data == 'battery_replacement':
        description = "🔋 **Заміна батареї**\n\nШвидко розряджається телефон? Ми замінимо батарею на нову, щоб ваш пристрій працював довше. Тривалість заміни - до 1 години."
    elif call.data == 'charging_port_repair':
        description = "🔌 **Ремонт роз'єму зарядки**\n\nВаш телефон не заряджається належним чином? Ми виправимо або замінимо роз'єм зарядки, щоб ваш пристрій працював як новий."
    elif call.data == 'other_issue':
        description = "📞 **Інша поломка**\n\nЯкщо у вас інша проблема з телефоном, надішліть нам опис, і ми допоможемо знайти найкраще рішення."

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Записатися", callback_data='register_' + call.data))

    bot.send_message(
        call.message.chat.id,
        description,
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('register_'))
def register(call):
    request_user_info(call.message)

def request_user_info(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Назад")
    bot.send_message(
        message.chat.id,
        "Будь ласка, надішліть наступну інформацію для запису:\n- Ваше ім'я\n- Номер телефону\n- Модель телефону\n- Опис проблеми",
        reply_markup=markup
    )
    bot.register_next_step_handler(message, process_order)

def get_status(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Назад")
    bot.send_message(
        message.chat.id,
        "Введіть номер вашого замовлення для перевірки статусу ремонту:",
        reply_markup=markup
    )

def get_about(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Назад")
    bot.send_photo(message.chat.id, photo=open('./photos/2.png', 'rb'))
    bot.send_message(
        message.chat.id,
        "Ми - професійна майстерня з ремонту телефонів з багаторічним досвідом роботи. "
        "Пропонуємо швидкий та якісний ремонт різних моделей телефонів. "
        "Наша мета - зробити ваш пристрій знову як новий!",
        reply_markup=markup
    )

def get_contacts(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Назад")
    bot.send_message(
        message.chat.id,
        "Наша майстерня знаходиться за адресою: проспект Степана Бандери, 4, Київ.\n"
        "Графік роботи: Пн-Пт з 9:00 до 18:00.\nТелефон для довідок: +380123456789",
        reply_markup=markup
    )

def get_categories(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Діагностика", callback_data='diagnostics'))
    markup.add(types.InlineKeyboardButton("Заміна екрана", callback_data='screen_replacement'))
    markup.add(types.InlineKeyboardButton("Заміна батареї", callback_data='battery_replacement'))
    markup.add(types.InlineKeyboardButton("Ремонт роз'єму зарядки", callback_data='charging_port_repair'))
    markup.add(types.InlineKeyboardButton("Інша поломка", callback_data='other_issue'))

    back_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back_markup.add("Назад")

    bot.send_message(
        message.chat.id,
        "Оберіть категорію послуг для перегляду інформації та запису:",
        reply_markup=markup
    )
    bot.send_message(
        message.chat.id,
        "Для повернення натисніть кнопку 'Назад'",
        reply_markup=back_markup
    )

def process_order(message):
    if message.text == "Назад":
        main_menu(message)
        return
    user_data = message.text.split('\n')
    if len(user_data) < 4:
        bot.send_message(
            message.chat.id,
            "Недостатньо даних. Переконайтесь, що ви надали ім'я, номер телефону, модель телефону та опис проблеми."
        )
        return request_user_info(message)

    name = user_data[0]
    phone = user_data[1]
    phone_model = user_data[2]
    problem_description = user_data[3]

    order_number = str(random.randint(10000, 99999))
    order_status_db[order_number] = {
        "status": "Замовлення прийнято на обробку. Очікуйте подальших оновлень.",
        "name": name,
        "phone": phone,
        "phone_model": phone_model,
        "problem_description": problem_description
    }

    bot.send_message(
        message.chat.id,
        f"Дякуємо за запис! Ваш номер замовлення: {order_number}. Ви можете перевірити статус у розділі 'Статус ремонту'."
    )
@bot.message_handler(content_types=['text'])
def handle_order_status_request(message):
    if message.text.isdigit():
        order_info = order_status_db.get(message.text)
        if order_info:
            response = (
                f"Статус вашого замовлення: {order_info['status']}\n"
                f"Ім'я: {order_info['name']}\n"
                f"Телефон: {order_info['phone']}\n"
                f"Модель телефону: {order_info['phone_model']}\n"
                f"Опис проблеми: {order_info['problem_description']}"
            )
        else:
            response = "Замовлення з таким номером не знайдено."
        bot.send_message(message.chat.id, response)
bot.polling(none_stop=True)
