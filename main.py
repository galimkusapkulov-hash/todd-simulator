import asyncio
import logging
import random
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiohttp import web

# Токен берем из переменных окружения (для безопасности) или вставляй строкой
BOT_TOKEN = os.getenv("BOT_TOKEN", "ТВОЙ_ТЕЛЕГРАМ_ТОКЕН")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

TODD_QUOTES = [
    "Слышь, купи Скайрим. Там теперь можно грабить корованы, и он идет на твоем тостере.",
    "В нашей новой игре будет 16-кратно увеличенная детализация. Вы сможете зайти в каждое здание!",
    "Видите ту гору? Вы можете на неё взойти. Это не декорация.",
    "Она просто работает (It just works). Если вы видите баг — это не баг, это неожиданная геймплейная фича.",
    "Мы переиздаем TES V: Skyrim на умные холодильники и дисплеи стиральных машин. Предзаказ уже открыт.",
    "Новый движок? Зачем? Наш Creation Engine еще готов пережить пару поколений консолей.",
]

@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    welcome_text = (
        "🕶️ *Тодд Говард заходит в чат в кожаной куртке.*\n\n"
        "Привет! Я Тодд Говард. **Оно просто работает.**\n\n"
        "Пиши мне что угодно, но лучший выбор — это предзаказ нового Скайрима."
    )
    await message.answer(welcome_text, parse_mode="Markdown")

@dp.message()
async def todd_talk(message: Message):
    response = random.choice(TODD_QUOTES)
    await message.reply(f"🕶️: {response}")

# Хэндлер для Render, чтобы сервер думал, что мы живы
async def handle_ping(request):
    return web.Response(text="It just works!")

async def start_webserver():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    # Render дает порт в переменную окружения PORT
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    # Запускаем веб-сервер параллельно с ботом
    await start_webserver()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
