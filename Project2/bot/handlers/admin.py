from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from config import ADMIN_IDS
from bot.handlers.user import OrderStates
from aiogram import Bot
from bot.handlers.user import products  # Імпорт списку товарів з user.py
from bot.database import session, Product, Order  # Імпорт бази даних і моделі


router = Router()
# Глобальний список товарів
products = []

class AdminStates(StatesGroup):
    waiting_for_item_name = State()
    waiting_for_item_price = State()
    waiting_for_item_description = State()
    waiting_for_item_stock = State()

@router.message(F.text == "/add_item", F.from_user.id.in_(ADMIN_IDS))
async def start_adding_item(message: Message, state: FSMContext):
    await message.answer("Введіть назву товару:")
    await state.set_state(AdminStates.waiting_for_item_name)

@router.message(AdminStates.waiting_for_item_name, F.from_user.id.in_(ADMIN_IDS))
async def add_item_name(message: Message, state: FSMContext):
    await state.update_data(item_name=message.text)
    await message.answer("Тепер введіть ціну товару:")
    await state.set_state(AdminStates.waiting_for_item_price)

@router.message(AdminStates.waiting_for_item_price, F.from_user.id.in_(ADMIN_IDS))
async def add_item_price(message: Message, state: FSMContext):
    try:
        price = float(message.text)
    except ValueError:
        await message.answer("Ціна повинна бути числом. Спробуйте ще раз:")
        return

    await state.update_data(price=price)
    await message.answer("Введіть опис товару:")
    await state.set_state(AdminStates.waiting_for_item_description)

@router.message(AdminStates.waiting_for_item_description, F.from_user.id.in_(ADMIN_IDS))
async def add_item_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Чи є товар у наявності? Відповідайте 'Так' або 'Ні'.")
    await state.set_state(AdminStates.waiting_for_item_stock)

@router.message(AdminStates.waiting_for_item_stock, F.from_user.id.in_(ADMIN_IDS))
async def add_item_stock(message: Message, state: FSMContext):
    in_stock = message.text.lower() in ["так", "yes", "y"]
    data = await state.get_data()

    # Додаємо товар у базу даних
    new_product = Product(
        name=data['item_name'],
        price=data['price'],
        description=data['description'],
        in_stock=in_stock
    )
    session.add(new_product)
    session.commit()

    await message.answer(f"Товар '{data['item_name']}' успішно додано.")
    await state.clear()

@router.message(F.text == "/admin", F.from_user.id.in_(ADMIN_IDS))
async def admin_panel(message: Message):
    await message.answer("Панель адміністратора:\n"
                         "/add_item - Додати товар\n"
                         "/remove_item - Видалити товар\n"
                         "/orders - Список замовлень")

@router.message(OrderStates.waiting_for_delivery_type, F.text == "Підтвердити")
async def confirm_order(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    product = data.get("selected_product")
    contact = data.get("contact")

    # Надсилання підтвердження користувачу
    await message.answer(
        f"Дякуємо за ваше замовлення!\n"
        f"Товар: {product['name']}\n"
        f"Ціна: {product['price']}\n"
        f"Контактний номер: {contact}\n"
        f"Наш менеджер зв'яжеться з вами найближчим часом."
    )

    # Відправка повідомлення адміністраторам
    admin_message = (
        f"Нове замовлення:\n\n"
        f"Товар: {product['name']}\n"
        f"Ціна: {product['price']}\n"
        f"Контактний номер клієнта: {contact}\n"
        f"Користувач: {message.from_user.full_name} (ID: {message.from_user.id})"
    )
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, admin_message)
        except Exception as e:
            print(f"Не вдалося надіслати повідомлення адміністратору {admin_id}: {e}")

    # Вихід у головне меню
    await message.answer(
        "Вас повернуто до головного меню.",
        reply_markup=main_menu()
    )
    await state.clear()  # Очищуємо стан

@router.message(F.text == "/remove_item", F.from_user.id.in_(ADMIN_IDS))
async def start_remove_item(message: Message):
    """
    Показує список товарів із кнопками для видалення.
    """
    products = session.query(Product).all()

    if not products:
        await message.answer("Каталог порожній. Немає товарів для видалення.")
        return

    # Генеруємо кнопки для кожного товару
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"{product.name} ({product.price:.2f} грн)", callback_data=f"delete_{product.id}")]
            for product in products
        ]
    )

    await message.answer("Оберіть товар для видалення:", reply_markup=markup)

@router.callback_query(F.data.startswith("delete_"))
async def remove_item(callback: CallbackQuery):
    """
    Видаляє товар із бази даних.
    """
    product_id = int(callback.data.split("_")[1])

    # Отримуємо товар із бази
    product = session.query(Product).filter(Product.id == product_id).first()

    if not product:
        await callback.message.answer("Товар не знайдено або вже видалений.")
        await callback.answer()
        return

    # Видаляємо товар із бази
    session.delete(product)
    session.commit()

    await callback.message.answer(f"Товар '{product.name}' успішно видалено.")
    await callback.answer()

@router.message(F.text == "/orders", F.from_user.id.in_(ADMIN_IDS))
async def view_orders(message: Message):
    """
    Відображає всі замовлення для адміністраторів.
    """
    orders = session.query(Order).all()

    if not orders:
        await message.answer("Наразі немає жодного замовлення.")
        return

    # Формуємо список замовлень
    order_list = [
        f"🆔 Замовлення #{order.id}\n"
        f"👤 Ім'я: {order.name}\n"
        f"📞 Телефон: {order.phone}\n"
        f"🏠 Адреса: {order.address}\n"
        f"🚚 Доставка: {order.delivery_type}\n"
        f"💰 Сума: {order.total_price:.2f} грн\n"
        f"🕒 Дата: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        for order in orders
    ]

    await message.answer("\n\n".join(order_list))
