from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [213805079]

STRIPE_API_KEY = "sk_test_51QXAxFFJ9MG6rFfBEJlc5E7nOTMrsAEg5vojMoBqDtcv5qwGwVyz8jZaTzAArhipyENTrieo81Hw0qgliaP7xANJ00SoM0XE8K"
STRIPE_SUCCESS_URL = "https://telegram.me/your_bot_username"
STRIPE_CANCEL_URL = "https://telegram.me/your_bot_username"
