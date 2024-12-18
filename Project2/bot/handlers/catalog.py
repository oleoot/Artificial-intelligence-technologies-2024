from aiogram import Router, F
from aiogram.types import CallbackQuery
from bot.keyboards.inline import catalog_buttons, order_buttons

router = Router()

@router.message(F.text == "/catalog")
async def catalog_command(message: Message):
    await message.answer("Ось список доступних товарів:", reply_markup=catalog_buttons())

@router.callback_query(F.data.startswith("item_"))
async def catalog_item(callback: CallbackQuery):
    item_id = callback.data.split("_")[1]
    await callback.message.answer(f"Ви переглядаєте товар {item_id}", reply_markup=order_buttons())

@router.callback_query(F.data == "order_confirm")
async def confirm_order(callback: CallbackQuery):
    await callback.message.answer("Ваше замовлення підтверджено! Адміністратор зв'яжеться з вами.")
