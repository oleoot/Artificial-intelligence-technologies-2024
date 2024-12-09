import cv2
import numpy as np
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram import F
from aiogram.filters import Command
from aiogram import Router

# Токен вашого бота
API_TOKEN = '7610559949:AAHayg6kG09RzUO9xnH9kDKH_K560wHQl3Q'

# Ініціалізація бота та диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()

# Функція для виявлення облич
def detect_faces(image_path):
    # Завантаження попередньо навченого каскадного класифікатора
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt.xml')

    # Завантаження зображення
    image = cv2.imread(image_path)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Виявлення облич
    faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5)

    # Малювання прямокутників навколо виявлених облич
    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)

    # Збереження обробленого зображення
    output_path = 'PR9/output.jpg'
    cv2.imwrite(output_path, image)

    return output_path, len(faces)

@router.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer(
        "Привіт! Я бот для розпізнавання облич на фотографіях. Відправ мені фото, і я знайду всі обличчя на ньому. "
        "Після цього я поверну тобі оброблене зображення з виділеними обличчями. Просто відправ фото, щоб почати!"
    )

@router.message(F.photo)
async def process_photo(message: types.Message):
    print("Фото отримано")
    # Отримання файлу з фото
    photo = message.photo[-1]
    file_id = photo.file_id
    file = await bot.get_file(file_id)

    # Завантаження файлу
    await bot.download_file(file.file_path, 'PR9/input.jpg')

    # Виклик функції для виявлення облич
    processed_image_path, face_count = detect_faces('PR9/input.jpg')

    # Відправка обробленого зображення назад користувачу
    with open(processed_image_path, 'rb') as image_file:
        await message.answer_photo(photo=image_file)

    # Відправка повідомлення з кількістю виявлених облич
    await message.answer(f"Розпізнано {face_count} облич(я) на фото.")

    # Видалення тимчасових файлів
    os.remove('PR9/input.jpg')
    os.remove(processed_image_path)

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
