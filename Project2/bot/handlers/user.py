from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from bot.keyboards.inline import catalog_buttons, product_details
from bot.keyboards.reply import main_menu, main_menu_reply
from bot.database import session, Product, Order  # Імпорт бази даних і моделі
import stripe
from config import STRIPE_API_KEY, STRIPE_SUCCESS_URL, STRIPE_CANCEL_URL

stripe.api_key = STRIPE_API_KEY

router = Router()

# Словник для кошиків
user_cart = {}

# Список товарів
products = [
    {"id": 1, "name": "Смартфон Samsung Galaxy S23", "price": "30,000 грн"},
    {"id": 2, "name": "Ноутбук Apple MacBook Pro 14", "price": "80,000 грн"},
    {"id": 3, "name": "Навушники Sony WH-1000XM5", "price": "12,000 грн"},
    {"id": 4, "name": "Телевізор LG OLED 55\" 4K", "price": "50,000 грн"},
]

# Стан машини станів для оформлення замовлення
class OrderStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_address = State()
    waiting_for_delivery_type = State()
    waiting_for_payment = State()

@router.message(F.text == "/start")
async def main_menu(message: Message):
    """
    Відображає головне меню у Reply-клавіатурі.
    """
    await message.answer("Привіт! Я ваш бот. Ось, що я вмію:\n"
        "/help - Список команд\n"
        "/catalog - Переглянути товари\n"
        "/info - Про бота",
        reply_markup=main_menu_reply())

# Вибір товару
@router.message(F.text == "Каталог")
async def show_catalog(message: Message):
    """
    Відображає список товарів із кнопкою "Переглянути товар".
    """
    products = session.query(Product).all()  # Витягуємо об'єкти Product із бази даних

    if not products:
        await message.answer("Каталог поки що порожній.")
        return

    # Відображаємо кожен товар із кнопкою "Переглянути товар"
    for product in products:
        await message.answer(
            f"{product.name} - {product.price:.2f} грн",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(
                        text="Переглянути товар 🔍",
                        callback_data=f"view_product_{product.id}"
                    )]
                ]
            )
        )
@router.callback_query(F.data.startswith("view_product_"))
async def view_product(callback: CallbackQuery):
    """
    Відображає повну інформацію про товар із кнопкою "Додати в кошик".
    """
    product_id = int(callback.data.split("_")[2])
    product = session.query(Product).filter(Product.id == product_id).first()

    if not product:
        await callback.message.answer("Товар не знайдено.")
        await callback.answer()
        return

    availability = "✅ Є в наявності" if product.in_stock else "❌ Немає в наявності"

    await callback.message.answer(
        f"Назва: {product.name}\n"
        f"Ціна: {product.price:.2f} грн\n"
        f"Опис: {product.description}\n"
        f"Наявність: {availability}\n\n"
        "Щоб додати цей товар у кошик, натисніть кнопку нижче:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text="Додати в кошик 🛒",
                    callback_data=f"add_to_cart_{product.id}"
                )],
                [InlineKeyboardButton(
                    text="⬅️ Повернутись до каталогу",
                    callback_data="open_catalog"
                )]
            ]
        )
    )
    await callback.answer()

@router.callback_query(F.data.startswith("add_to_cart_"))
async def add_to_cart(callback: CallbackQuery):
    """
    Додає товар у кошик користувача.
    """
    product_id = int(callback.data.split("_")[3])
    product = session.query(Product).filter(Product.id == product_id).first()

    if not product:
        await callback.message.answer("Товар не знайдено або більше недоступний.")
        await callback.answer()
        return

    # Додаємо товар у словник кошика
    user_id = callback.from_user.id
    if user_id not in user_cart:
        user_cart[user_id] = []
    user_cart[user_id].append(product)

    await callback.message.answer(f"Товар '{product.name}' додано до вашого кошика 🛒")
    await callback.answer()
def catalog_menu():
    """
    Генерує Reply-клавіатуру з кнопкою 'Каталог'.
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Каталог")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

@router.message(F.text == "Кошик 🛒")
async def view_cart(message: Message):
    """
    Відображає товари у кошику користувача.
    """
    user_id = message.from_user.id
    cart = user_cart.get(user_id, [])

    if not cart:
        await message.answer("Ваш кошик порожній 🛒")
        return

    # Генеруємо список товарів із кнопками "Видалити"
    for idx, product in enumerate(cart):
        await message.answer(
            f"{product.name} - {product.price:.2f} грн",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(
                        text="Видалити ❌", callback_data=f"remove_from_cart_{idx}"
                    )]
                ]
            )
        )

    total_price = sum(product.price for product in cart)

    # Підсумок кошика
    await message.answer(
        f"Загальна сума: {total_price:.2f} грн\n"
        "Ви можете оформити замовлення або продовжити покупки.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Оформити замовлення ✅", callback_data="checkout")],
                [InlineKeyboardButton(text="⬅️ Повернутись до каталогу", callback_data="open_catalog")]
            ]
        )
    )

@router.callback_query(F.data.startswith("remove_from_cart_"))
async def remove_from_cart(callback: CallbackQuery):
    """
    Видаляє товар із кошика користувача.
    """
    user_id = callback.from_user.id
    cart = user_cart.get(user_id, [])

    # Отримуємо індекс товару для видалення
    item_index = int(callback.data.split("_")[3])

    # Перевірка індексу
    if item_index < 0 or item_index >= len(cart):
        await callback.message.answer("Помилка: товар не знайдено в кошику.")
        await callback.answer()
        return

    # Видаляємо товар
    removed_item = cart.pop(item_index)
    user_cart[user_id] = cart  # Оновлюємо кошик

    # Повідомляємо про успішне видалення
    await callback.message.answer(f"Товар '{removed_item.name}' видалено з кошика 🛒")

    # Повторно показуємо оновлений кошик
    await view_cart(callback)
    await callback.answer()


@router.message(F.text == "/order")
async def order_command(message: Message):
    """
    Обробник для команди /order.
    Виводить кнопку для переходу в каталог.
    """
    await message.answer(
        "Щоб зробити замовлення, перейдіть до каталогу:",
        reply_markup=catalog_menu()  # Додаємо клавіатуру
    )

@router.message(F.text == "Допомога")
async def show_help(message: Message):
    """
    Відображає довідку про команди бота.
    """
    await message.answer(
        "❓ Допомога:\n"
        "/start - Перезапустити бот\n"
        "Каталог - Переглянути список товарів\n"
        "Кошик - Переглянути товари у кошику\n"
        "Інформація - Деталі про бота\n"
        "Допомога - Довідка по командам"
    )

@router.message(F.text == "Інформація")
async def info_command(message: Message):
    await message.answer("Це бот для перегляду каталогу товарів та оформлення замовлень. Зв'яжіться з адміністратором для більшої інформації.")

@router.callback_query(F.data.startswith("order_"))
async def order_product(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    product = session.query(Product).filter(Product.id == product_id).first()

    if not product:
        await callback.message.answer("Цей товар більше недоступний для замовлення.")
        await callback.answer()
        return

    # Додаємо замовлення в базу даних
    new_order = Order(
        product_name=product.name,
        price=product.price,
        user_id=callback.from_user.id,
        user_name=callback.from_user.full_name
    )
    session.add(new_order)
    session.commit()

    # Відповідаємо користувачу
    await callback.message.answer(
        f"Ваше замовлення прийнято:\n"
        f"Назва: {product.name}\n"
        f"Ціна: {product.price:.2f} грн\n\n"
        "Наш менеджер зв'яжеться з вами найближчим часом!"
    )
    await callback.answer()


@router.callback_query(F.data == "open_catalog")
async def open_catalog(callback: CallbackQuery):
    """
    Повертає користувача до каталогу товарів.
    """
    await show_catalog(callback.message)  # Передаємо Message об'єкт у show_catalog
    await callback.answer()

@router.callback_query(F.data == "checkout")
async def checkout(callback: CallbackQuery, state: FSMContext):
    """
    Запускає процес оформлення замовлення, запитуючи ім'я.
    """
    await callback.message.answer("Будь ласка, введіть ваше ім'я:")
    await state.set_state(OrderStates.waiting_for_name)
    await callback.answer()

@router.message(OrderStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    """
    Зберігає ім'я користувача та запитує номер телефону.
    """
    await state.update_data(name=message.text)

    await message.answer("Введіть ваш номер телефону у форматі +380XXXXXXXXX:")
    await state.set_state(OrderStates.waiting_for_phone)

@router.message(OrderStates.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    """
    Зберігає номер телефону та запитує адресу доставки.
    """
    if not message.text.startswith("+") or not message.text[1:].isdigit():
        await message.answer("Некоректний номер телефону. Спробуйте ще раз:")
        return

    await state.update_data(phone=message.text)

    await message.answer("Введіть вашу адресу доставки:")
    await state.set_state(OrderStates.waiting_for_address)

@router.message(OrderStates.waiting_for_address)
async def process_address(message: Message, state: FSMContext):
    """
    Зберігає адресу доставки та запитує тип доставки.
    """
    await state.update_data(address=message.text)

    # Запит типу доставки через кнопки
    delivery_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Експрес")],
            [KeyboardButton(text="Стандартна")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await message.answer("Оберіть тип доставки:", reply_markup=delivery_keyboard)
    await state.set_state(OrderStates.waiting_for_delivery_type)

@router.message(OrderStates.waiting_for_delivery_type)
async def process_delivery_type(message: Message, state: FSMContext):
    """
    Зберігає тип доставки, генерує посилання на оплату через Stripe.
    """
    if message.text not in ["Експрес", "Стандартна"]:
        await message.answer("Будь ласка, оберіть 'Експрес' або 'Стандартна'.")
        return

    await state.update_data(delivery_type=message.text)

    # Отримуємо дані замовлення
    user_data = await state.get_data()

    # Розрахунок загальної суми
    total_price = sum(item.price for item in user_cart.get(message.from_user.id, []))  # Загальна сума

    # Генеруємо посилання через Stripe
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"Замовлення для {user_data['name']}",
                        },
                        "unit_amount": int(total_price * 100),  # Stripe працює з копійками
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
        )

        # Відправляємо посилання на оплату
        await message.answer(
            f"✅ Ваше замовлення майже оформлено!\n"
            f"Сума до оплати: {total_price:.2f} USD\n\n"
            f"!Після успішної оплати напишіть 'Я оплатив' для підтвердження замовлення!\n"
            f"[Натисніть тут для оплати]({session.url})",
            parse_mode="Markdown",
        )

        # Встановлюємо стан очікування оплати
        await state.set_state(OrderStates.waiting_for_payment)

    except stripe.error.StripeError as e:
        await message.answer("❌ Виникла помилка під час створення посилання на оплату. Спробуйте пізніше.")
        print(f"Stripe error: {e}")


@router.message(OrderStates.waiting_for_payment)
async def confirm_payment(message: Message, state: FSMContext):
    """
    Завершує оформлення замовлення після оплати.
    """
    if message.text.lower() != "я оплатив":
        await message.answer("Будь ласка, введіть 'Я оплатив', щоб підтвердити оплату.")
        return

    # Отримуємо дані замовлення
    user_data = await state.get_data()
    user_id = message.from_user.id
    cart = user_cart.pop(user_id, [])

    if not cart:
        await message.answer("Ваш кошик порожній.")
        await state.clear()
        return

    # Розрахунок загальної суми
    total_price = sum(item.price for item in cart)

    # Збереження замовлення у базу даних
    new_order = Order(
        user_id=user_id,
        name=user_data['name'],
        phone=user_data['phone'],
        address=user_data['address'],
        delivery_type=user_data['delivery_type'],
        total_price=total_price
    )
    session.add(new_order)
    session.commit()

    # Підсумкове повідомлення
    await message.answer(
        f"✅ Оплата підтверджена!\n\n"
        f"**Ім'я:** {user_data['name']}\n"
        f"**Телефон:** {user_data['phone']}\n"
        f"**Адреса:** {user_data['address']}\n"
        f"**Тип доставки:** {user_data['delivery_type']}\n"
        f"**Сума:** {total_price:.2f} грн\n\n"
        "Дякуємо за ваше замовлення! Наш менеджер зв'яжеться з вами.",
        reply_markup=main_menu_reply()
    )

    # Завершуємо FSM
    await state.clear()
