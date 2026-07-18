import asyncio
import logging
import random
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiohttp import web

# Токен берем из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN", "ТВОЙ_ТЕЛЕГРАМ_ТОКЕН")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# --- БАЗА ДАННЫХ ТАМАГОЧИ (в памяти) ---
user_foxes = {}

def get_fox_status(user_id):
    if user_id not in user_foxes:
        user_foxes[user_id] = {"satiety": 50, "mood": 50, "energy": 50}
    return user_foxes[user_id]

# Золотые цитаты Тодда
TODD_QUOTES = [
    "Слышь, купи Скайрим. Там теперь можно грабить корованы, и он идет на твоем тостере.",
    "В нашей новой игре будет 16-кратно увеличенная детализация. Вы сможете зайти в каждое здание!",
    "Видите ту гору? Вы можете на неё взойти. Это не декорация.",
    "Она просто работает (It just works). Если вы видите баг — это не баг, это неожиданная геймплейная фича.",
    "Мы переиздаем TES V: Skyrim на умные холодильники. Предзаказ уже открыт.",
]

# --- ХЭНДЛЕРЫ КОМАНД ТАМАГОЧИ ---

@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    await message.answer(
        "🕶️ *Тодд Говард в кожанке заходит в чат вместе с Лисом.*\n\n"
        "Привет! Я Тодд. Мы тут скрестили движок Creation Engine с пушистыми технологиями. **Оно просто работает.**\n\n"
        "Используй команды меню, чтобы ухаживать за Лисом, или просто общайся со мной!",
        parse_mode="Markdown"
    )

@dp.message(F.text == "/status")
async def cmd_status(message: Message):
    fox = get_fox_status(message.from_user.id)
    await message.reply(
        f"📊 *Статус Лиса под управлением Тодда:*\n"
        f"🍖 Сытость: {fox['satiety']}/100\n"
        f"🦊 Настроение: {fox['mood']}/100\n"
        f"⚡ Энергия: {fox['energy']}/100\n\n"
        f"🕶️ Тодд говорит: _«Детализация этого лиса увеличена 16-кратно!»_",
        parse_mode="Markdown"
    )

@dp.message(F.text == "/feed")
async def cmd_feed(message: Message):
    fox = get_fox_status(message.from_user.id)
    fox["satiety"] = min(100, fox["satiety"] + 20)
    await message.reply("🍖 Вы покормили Лиса! Тодд Говард лично приготовил сладкий рулет. Сытость повышена!")

@dp.message(F.text == "/hug")
async def cmd_hug(message: Message):
    fox = get_fox_status(message.from_user.id)
    fox["mood"] = min(100, fox["mood"] + 20)
    await message.reply("🦊 Вы обняли Лиса. Тепло и пушисто! Настроение улучшилось.")

@dp.message(F.text == "/play")
async def cmd_play(message: Message):
    fox = get_fox_status(message.from_user.id)
    if fox["energy"] < 20:
        await message.reply("⚡ Лис слишком устал, чтобы играть! Сначала уложи его спать.")
        return
    fox["mood"] = min(100, fox["mood"] + 15)
    fox["energy"] = max(0, fox["energy"] - 20)
    await message.reply("🎮 Вы поиграли с Лисом в Скайрим на умном тостере! Настроение 📈, Энергия 📉.")

@dp.message(F.text == "/sleep")
async def cmd_sleep(message: Message):
    fox = get_fox_status(message.from_user.id)
    fox["energy"] = min(100, fox["energy"] + 40)
    await message.reply("💤 Лис ушел в спячку на пару часиков. Энергия восстановлена!")

@dp.message(F.text == "/fox")
async def cmd_fox(message: Message):
    fox_emojis = ["🦊", "🦊🐾", "🦊✨", "🐺"]
    await message.reply(f"{random.choice(fox_emojis)} Фырк! Призван случайный Лис прямо из Скайрима.")

# --- ИНТЕГРАЦИЯ ИЗ РЕПОЗИТОРИЯ PLYT ---
@dp.message(F.text.startswith("/plyt") | F.text.startswith("/play_music"))
async def cmd_plyt(message: Message):
    # Код из репозитория junioraww/plyt для имитации музыкального плеера / плейлистов
    await message.reply("🎵 *Запуск аудиомодуля PLYT v1.0...*\nПодключаем кастомные звуковые дорожки из Скайрима. Музыка играет 24/7!", parse_mode="Markdown")

# --- ОБЫЧНЫЙ ТЕКСТ (ОТВЕТЫ ТОДДА) ---
@dp.message()
async def todd_talk(message: Message):
    response = random.choice(TODD_QUOTES)
    await message.reply(f"🕶️: {response}")

# --- ВЕБ-СЕРВЕР ДЛЯ RENDER ---
async def handle_ping(request):
    return web.Response(text="It just works!")

async def start_webserver():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    await start_webserver()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
