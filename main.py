import asyncio
import os
import logging
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from google import genai
from google.genai import types as genai_types

# Загружаем переменные окружения
load_dotenv()

TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# Настройка логов
logging.basicConfig(level=logging.INFO)

# Инициализация Gemini
gemini_client = genai.Client(api_key=GEMINI_KEY)

# Хранилище сессий чата для сохранения контекста переписки
# Структура: {chat_id: chat_session}
user_chats = {}

# Инициализация Telegram бота
bot = Bot(
    token=TG_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Приветствие и сброс контекста при старте."""
    chat_id = message.chat.id
    # Создаём новую сессию чата Gemini для пользователя
    user_chats[chat_id] = gemini_client.chats.create(model="gemini-2.5-flash")
    
    await message.answer(
        "Привет! Я твой личный Gemini-клиент.\n\n"
        "Просто напиши мне сообщение, и я отвечу. "
        "Чтобы сбросить контекст диалога и начать заново, используй /reset."
    )


@dp.message(Command("reset"))
async def cmd_reset(message: types.Message):
    """Сброс истории диалога."""
    chat_id = message.chat.id
    user_chats[chat_id] = gemini_client.chats.create(model="gemini-2.5-flash")
    await message.answer("История диалога очищена! Начинаем с чистого листа.")


@dp.message()
async def handle_message(message: types.Message):
    """Обработка текстовых сообщений."""
    chat_id = message.chat.id

    # Если сессия ещё не создана, создаём
    if chat_id not in user_chats:
        user_chats[chat_id] = gemini_client.chats.create(model="gemini-2.5-flash")

    # Показываем статус «печатает...» в Telegram
    await bot.send_chat_action(chat_id=chat_id, action="typing")

    try:
        # Отправляем текст в Gemini в рамках текущей сессии
        response = user_chats[chat_id].send_message(message.text)
        
        # Отправляем ответ пользователю
        await message.answer(response.text)
        
    except Exception as e:
        logging.error(f"Ошибка при запросе к Gemini: {e}")
        await message.answer("Упс, произошла ошибка при обработке запроса.")


async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
