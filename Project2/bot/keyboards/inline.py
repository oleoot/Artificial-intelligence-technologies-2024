from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def catalog_buttons(products):
    """
    Генерує інлайн-кнопки для кожного товару в каталозі.
    """
    buttons = [
        [InlineKeyboardButton(
            text=f"{product.name} ({product.price:.2f} грн)",
            callback_data=f"add_to_cart_{product.id}"
        )]
        for product in products
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def product_details(product_id):
    """
    Клавіатура для товару з кнопкою замовлення.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Замовити", callback_data=f"order_{product_id}")],
            [InlineKeyboardButton(text="Повернутись до каталогу", callback_data="return_to_catalog")]
        ]
    )

def order_buttons():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Замовити", callback_data="order_confirm")]
    ])
