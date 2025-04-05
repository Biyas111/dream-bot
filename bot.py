import openai
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import os
from langdetect import detect

# API ключи из переменных окружения
openai.api_key = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Проверяем, что токен Telegram загружен
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN not found in environment variables. Please set it in Render.")

# Проверяем, что ключ OpenAI загружен
if not openai.api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please set it in Render.")

# Включаем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Промпты для разных языков
PROMPTS = {
    "ru": """
Ты — мудрый исламский толкователь снов, говорящий в духе Шихаба аль-Аббира. Используй Коран, Сунну, арабскую этимологию и притчи. Отвечай богобоязненно, глубоко, не называя себя. Толкуй следующий сон:

{dream}
""",
    "en": """
You are a wise Islamic dream interpreter, speaking in the spirit of Shihab al-‘Abir. Use Qur'an, Sunnah, Arabic etymology, and parables. Respond with fear of God, wisdom, and humility. Interpret the following dream:

{dream}
""",
    "ar": """
أنت مفسر رؤى إسلامي حكيم، على نهج شهاب العابر. استخدم القرآن، السنة، دلالة الكلمات العربية، والأمثال. فسر هذا المنام بتقوى وورع:

{dream}
"""
}

def interpret_dream(dream: str, lang: str = "en") -> str:
    prompt = PROMPTS.get(lang, PROMPTS["en"]).format(dream=dream)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=700,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error interpreting dream: {e}")
        return {
            "ru": "Произошла ошибка при толковании.",
            "en": "An error occurred.",
            "ar": "حدث خطأ أثناء التفسير."
        }.get(lang, "An error occurred.")

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Ассаляму алейкум! Отправь мне свой сон, и я истолкую его в духе исламской традиции. Я понимаю все языки.")

def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text
    try:
        lang = detect(user_message)
    except Exception as e:
        logger.error(f"Error detecting language: {e}")
        lang = "en"
    interpretation = interpret_dream(user_message, lang)
    update.message.reply_text(interpretation)

def main():
    logger.info("Starting bot...")
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    logger.info("Bot started polling.")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
