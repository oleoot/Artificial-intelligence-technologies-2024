import telebot
import sqlite3
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

API_TOKEN = '7566867318:AAF0bWemq3rnXxw0LbUua1XN5dvWS2h2I_U'
bot = telebot.TeleBot(API_TOKEN)

# Ініціалізуємо базу даних SQLITE
conn = sqlite3.connect('store.db', check_same_thread=False)
cursor = conn.cursor()

# Створення таблиці замовлень, якщо вона не існує
cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    item_name TEXT
)''')
conn.commit()
# Створення таблиці користувачів, якщо вона не існує
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance REAL DEFAULT 100000
)''')
conn.commit()

# Ініціалізація базового каталогу товарів
catalog = [
    {"id": 1, "name": "Смартфон", "description": "Iphone 15 Pro Max", "price": 70000},
    {"id": 2, "name": "Ноутбук", "description": "Lenovo Legion 5", "price": 42000},
    {"id": 3, "name": "Навушники", "description": "AirPods Pro 2", "price": 8000},
    {"id": 4, "name": "Смарт-годинник", "description": "Samsung Galaxy Watch", "price": 8000},
    {"id": 5, "name": "Фен", "description": "Dyson D16 Supersonic", "price": 24000}
]
administrators = [213805079]

# Функція для обробки основних кнопок
main_reply_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
main_reply_keyboard.add(
    KeyboardButton("Каталог"),
    KeyboardButton("Замовити"),
    KeyboardButton("Допомога"),
    KeyboardButton("Інформація"),
    KeyboardButton("Відгуки"),
    KeyboardButton("Адміністрування")
)

# Вже наявні відгуки
feedbacks = [
    "Чудовий сервіс і швидка доставка!",
    "Купував тут смарт-годинник, дуже задоволений!",
    "Дякую за якісний товар і консультацію!",
    "Кращий магазин електроніки, рекомендую всім!",
    "Замовляв ноутбук, отримав вчасно і в ідеальному стані!"
]

# Команда: /start
@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, "Привіт! Я чат-бот магазину електроніки, використовуй кнопки нижче для навігація та роботи зі мною", reply_markup=main_reply_keyboard)

# Команда: /help
@bot.message_handler(commands=['help'])
@bot.message_handler(func=lambda message: message.text == "Допомога")
def help_command(message):
    help_text = (
        "<b>/catalog</b> - Переглянути каталог товарів\n"
        "<b>/order</b> - Оформити замовлення\n"
        "<b>/help</b> - Список доступних команд\n"
        "<b>/info</b> - Інформація про бота\n"
        "<b>/feedback</b> - Залишити відгук\n"
        "<b>/admin</b> - Меню адміністратора\n"
    )
    bot.send_message(message.chat.id, help_text, parse_mode="HTML", reply_markup=main_reply_keyboard)

# Команда: /info
@bot.message_handler(commands=['info'])
@bot.message_handler(func=lambda message: message.text == "Інформація")
def info_command(message):
    bot.send_message(
        message.chat.id,
        "Ласкаво просимо до нашого магазину електроніки! Ми пропонуємо широкий вибір гаджетів та техніки: смартфони, ноутбуки, навушники, смарт-годинники та багато іншого. Наші товари відрізняються високою якістю, а сервіс — швидкістю та надійністю!",
        reply_markup=main_reply_keyboard
    )

# Команда: /feedback
@bot.message_handler(commands=['feedback'])
@bot.message_handler(func=lambda message: message.text == "Відгуки")
def feedback_command(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text="Додати відгук", callback_data="add_feedback"))
    feedback_message = "\n".join(feedbacks)
    bot.send_message(
        message.chat.id,
        f"Ось що кажуть наші клієнти:\n{feedback_message}",
        reply_markup=markup
    )

# Обробка натискання кнопки "Додати відгук"
@bot.callback_query_handler(func=lambda call: call.data == "add_feedback")
def add_feedback_callback(call):
    bot.send_message(call.message.chat.id, "Введіть ваш відгук:")
    bot.register_next_step_handler(call.message, save_feedback)

# Збереження відгуку
def save_feedback(message):
    new_feedback = message.text.strip()
    if new_feedback:
        feedbacks.append(new_feedback)  # Додаємо відгук до масиву
        bot.send_message(message.chat.id, "Дякуємо за ваш відгук!", reply_markup=main_reply_keyboard)
    else:
        bot.send_message(message.chat.id, "Відгук не може бути порожнім. Спробуйте ще раз.", reply_markup=main_reply_keyboard)

# Команда: /catalog
@bot.message_handler(commands=['catalog'])
@bot.message_handler(func=lambda message: message.text == "Каталог")
def catalog_command(message):
    if not catalog:
        bot.send_message(message.chat.id, "Каталог поки що порожній.", reply_markup=main_reply_keyboard)
    else:
        markup = InlineKeyboardMarkup()
        for item in catalog:
            markup.add(InlineKeyboardButton(text=item['name'], callback_data=f"item_{item['id']}"))
        bot.send_message(message.chat.id, "Ось наші товари:", reply_markup=markup)

# Команда: /order
@bot.message_handler(commands=['order'])
@bot.message_handler(func=lambda message: message.text == "Замовити")
def order_command(message):
    if not catalog:
        bot.send_message(message.chat.id, "Каталог поки що порожній.", reply_markup=main_reply_keyboard)
    else:
        markup = InlineKeyboardMarkup()
        for item in catalog:
            markup.add(InlineKeyboardButton(text=item['name'], callback_data=f"order_{item['id']}"))
        bot.send_message(message.chat.id, "Оберіть товар для замовлення:", reply_markup=markup)

# Колбек для товарів з каталогу
@bot.callback_query_handler(func=lambda call: call.data.startswith("item_"))
def item_callback(call):
    item_id = int(call.data.split("_")[1])
    item = next((i for i in catalog if i['id'] == item_id), None)
    if item:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(text="Перейти до замовлення", callback_data=f"order_{item['id']}"))
        bot.send_message(call.message.chat.id, f"{item['name']}\nОпис: {item['description']}\nЦіна: {item['price']} грн", reply_markup=markup)
# Callback для оформлення замовлення
@bot.callback_query_handler(func=lambda call: call.data.startswith("order_"))
def order_item_callback(call):
    item_id = int(call.data.split("_")[1])
    item = next((i for i in catalog if i['id'] == item_id), None)
    if item:
        user_id = call.from_user.id
        user_balance = get_user_balance(user_id)

        if user_balance >= item['price']:
            # Списуємо гроші
            new_balance = user_balance - item['price']
            update_user_balance(user_id, new_balance)

            # Зберігаємо замовлення в базі даних
            cursor.execute("INSERT INTO orders (user_id, item_name) VALUES (?, ?)", (user_id, item['name']))
            conn.commit()

            bot.send_message(call.message.chat.id, f"Ваше замовлення '{item['name']}' підтверджено! З рахунку списано {item['price']} грн. Ваш поточний баланс: {new_balance} грн.", reply_markup=main_reply_keyboard)
            notify_admins(user_id, item['name'])
        else:
            bot.send_message(call.message.chat.id, f"Недостатньо коштів на рахунку. Ваш баланс: {user_balance} грн. Ціна товару: {item['price']} грн.", reply_markup=main_reply_keyboard)

# Сповіщення для адмінів
def notify_admins(user_id, item_name):
    for admin_id in administrators:
        bot.send_message(admin_id, f"Нове замовлення від {user_id}: {item_name}")

# Команда: /admin
@bot.message_handler(commands=['admin'])
@bot.message_handler(func=lambda message: message.text == "Адміністрування")
def admin_command(message):
    if message.from_user.id not in administrators:
        bot.send_message(message.chat.id, "Ви не маєте доступу до цієї команди.", reply_markup=main_reply_keyboard)
        return

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Додати товар"))
    markup.add(KeyboardButton("Видалити товар"))
    markup.add(KeyboardButton("Переглянути замовлення"))
    markup.add(KeyboardButton("Переглянути баланс"))
    bot.send_message(message.chat.id, "Меню адміністратора:", reply_markup=markup)
# Обробка команди додати товар
@bot.message_handler(func=lambda message: message.text == "Додати товар")
def add_item_command(message):
    bot.send_message(message.chat.id, "Введіть назву товару.")
    bot.register_next_step_handler(message, process_add_item_name)

def process_add_item_name(message):
    name = message.text
    bot.send_message(message.chat.id, "Введіть опис товару.")
    bot.register_next_step_handler(message, process_add_item_description, name)

def process_add_item_description(message, name):
    description = message.text
    bot.send_message(message.chat.id, "Введіть ціну товару.")
    bot.register_next_step_handler(message, process_add_item_price, name, description)

def process_add_item_price(message, name, description):
    try:
        price = float(message.text)
        item_id = len(catalog) + 1
        catalog.append({"id": item_id, "name": name, "description": description, "price": price})
        bot.send_message(message.chat.id, "Товар успішно додано!", reply_markup=main_reply_keyboard)
    except ValueError:
        bot.send_message(message.chat.id, "Будь ласка, введіть коректну ціну.", reply_markup=main_reply_keyboard)
# Обробка команди видалити товар
@bot.message_handler(func=lambda message: message.text == "Видалити товар")
def remove_item_command(message):
    if not catalog:
        bot.send_message(message.chat.id, "Каталог порожній.", reply_markup=main_reply_keyboard)
        return

    markup = InlineKeyboardMarkup()
    for item in catalog:
        markup.add(InlineKeyboardButton(text=item['name'], callback_data=f"remove_{item['id']}"))
    bot.send_message(message.chat.id, "Оберіть товар для видалення:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("remove_"))
def remove_item_callback(call):
    item_id = int(call.data.split("_")[1])
    global catalog
    catalog = [i for i in catalog if i['id'] != item_id]
    bot.send_message(call.message.chat.id, "Товар успішно видалено!", reply_markup=main_reply_keyboard)
# Обробка команди перегляду замовлення
@bot.message_handler(func=lambda message: message.text == "Переглянути замовлення")
def view_orders_command(message):
    cursor.execute("SELECT user_id, item_name FROM orders")
    orders = cursor.fetchall()
    if not orders:
        bot.send_message(message.chat.id, "Замовлень немає.", reply_markup=main_reply_keyboard)
        return

    order_list = "\n".join([f"Користувач {order[0]} замовив {order[1]}" for order in orders])
    bot.send_message(message.chat.id, f"Замовлення:\n{order_list}", reply_markup=main_reply_keyboard)
# Обробка команди перегляду балансу
@bot.message_handler(func=lambda message: message.text == "Переглянути баланс")
def view_balance_command(message):
    user_balance = get_user_balance(message.from_user.id)
    bot.send_message(message.chat.id, f"Ваш баланс: {user_balance} грн.", reply_markup=main_reply_keyboard)

# Автоматична відповідь на часті питання
@bot.message_handler(func=lambda message: True)  # Обробляємо всі повідомлення
def auto_reply(message):
    user_text = message.text.lower()  # Перетворюємо текст у нижній регістр для зручності перевірки

    # Визначаємо ключові слова та відповіді
    faq_responses = {
        "які товари доступні": "Щоб побачити доступні товари, скористайтесь командою /catalog або натисніть кнопку 'Каталог'.",
        "як зробити замовлення": "Для оформлення замовлення скористайтесь командою /order або натисніть кнопку 'Замовити'."
    }

    # Перевіряємо, чи є ключове слово в тексті
    for key, response in faq_responses.items():
        if key in user_text:
            bot.send_message(message.chat.id, response, reply_markup=main_reply_keyboard)
            return

    # Якщо питання не знайдено, відповідь за замовчуванням
    bot.send_message(message.chat.id, "Вибачте, я поки що не знаю відповіді на це питання. Спробуйте скористатись командою /help.", reply_markup=main_reply_keyboard)
def get_user_balance(user_id):
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        # Якщо користувач не знайдений, створюємо нового з початковим балансом
        initial_balance = 100000  # Початковий баланс
        cursor.execute("INSERT INTO users (user_id, balance) VALUES (?, ?)", (user_id, initial_balance))
        conn.commit()
        return initial_balance
def update_user_balance(user_id, new_balance):
    cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))
    conn.commit()
# Запускаємо бота
if __name__ == "__main__":
    bot.infinity_polling()
