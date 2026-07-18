const { Telegraf } = require('telegraf');
const express = require('express');
const axios = require('axios');

// Токен и настройки берём из переменных окружения Render
const BOT_TOKEN = process.env.BOT_TOKEN || "ТВОЙ_ТЕЛЕГРАМ_ТОКЕН";
// Если Оллама запущена локально и проброшена в сеть, или стоит на сервере:
const OLLAMA_URL = process.env.OLLAMA_URL || "http://localhost:11434/api/generate"; 

const bot = new Telegraf(BOT_TOKEN);
const app = express();
const PORT = process.env.PORT || 8080;

// Веб-сервер для пинга Render
app.get('/', (req, res) => {
    res.send('It just works! Todd + Plyt Engine JS v1.5');
});

// --- БАЗА ДАННЫХ В ПАМЯТИ (Пользователи, Опыт, Лисы) ---
const db = {};

function getUserData(userId) {
    if (!db[userId]) {
        db[userId] = {
            level: 1,
            xp: 0,
            fox: { satiety: 50, mood: 50, energy: 50 }
        };
    }
    return db[userId];
}

function addXp(userId, amount) {
    const user = getUserData(userId);
    user.xp += amount;
    const nextLevelXp = user.level * 100;
    if (user.xp >= nextLevelXp) {
        user.xp -= nextLevelXp;
        user.level += 1;
        return true; // Уровень повышен
    }
    return false;
}

const toddQuotes = [
    "Слышь, купи Скайрим. Там теперь можно грабить корованы, и он идет на твоем тостере.",
    "В нашей новой игре будет 16-кратно увеличенная детализация. Вы сможете зайти в каждое здание!",
    "Видите ту гору? Вы можете на неё взойти. Это не декорация.",
    "Она просто работает (It just works). Если вы видите баг — это не баг, это неожиданная геймплейная фича.",
    "Мы переиздаем TES V: Skyrim на умные холодильники. Предзаказ уже открыт."
];

// --- КОМАНДЫ БОТА ---

bot.start((ctx) => {
    ctx.replyWithMarkdown(
        "🕶️ *Тодд Говард и Лис приветствуют тебя в Plyt JS!*\n\n" +
        "Система опыта, уровней и тамагочи полностью функционирует. **Оно просто работает.**\n\n" +
        "Используй меню, чтобы следить за статами лиса!"
    );
});

bot.command('status', (ctx) => {
    const user = getUserData(ctx.from.id);
    ctx.replyWithMarkdown(
        `📊 *Твой профиль (Модули Levels & Fox):*\n` +
        `⭐ Уровень: ${user.level}\n` +
        `✨ Опыт (XP): ${user.xp}/${user.level * 100}\n\n` +
        `🍖 Сытость лиса: ${user.fox.satiety}/100\n` +
        `🦊 Настроение лиса: ${user.fox.mood}/100\n` +
        `⚡ Энергия лиса: ${user.fox.energy}/100\n\n` +
        `🕶️ _«16-кратная детализация твоего лиса!»_`
    );
});

bot.command('feed', (ctx) => {
    const user = getUserData(ctx.from.id);
    user.fox.satiety = Math.min(100, user.fox.satiety + 20);
    addXp(ctx.from.id, 15);
    ctx.reply("🍖 Вы покормили Лиса сладким рулетом от Тодда! Получено +15 XP.");
});

bot.command('hug', (ctx) => {
    const user = getUserData(ctx.from.id);
    user.fox.mood = Math.min(100, user.fox.mood + 20);
    addXp(ctx.from.id, 10);
    ctx.reply("🦊 Вы обняли Лиса! Он довольно фыркает в ответ. Получено +10 XP.");
});

bot.command('play', (ctx) => {
    const user = getUserData(ctx.from.id);
    if (user.fox.energy < 20) {
        return ctx.reply("⚡ Лис слишком устал. Уложи его спать с помощью команды /sleep.");
    }
    user.fox.mood = Math.min(100, user.fox.mood + 15);
    user.fox.energy = Math.max(0, user.fox.energy - 20);
    const leveledUp = addXp(ctx.from.id, 25);
    
    let text = "🎮 Вы поиграли с Лисом в Скайрим на тостере! Получено +25 XP.";
    if (leveledUp) text += `\n\n🎉 УРОВЕНЬ ПОВЫШЕН! Твой текущий уровень: ${user.level}!`;
    ctx.reply(text);
});

bot.command('sleep', (ctx) => {
    const user = getUserData(ctx.from.id);
    user.fox.energy = Math.min(100, user.fox.energy + 40);
    ctx.reply("💤 Лис ушел в спячку. Энергия восстановлена!");
});

bot.command('fox', (ctx) => {
    const emojis = ["🦊", "🦊🐾", "🦊✨", "🐺"];
    const randomEmoji = emojis[Math.floor(Math.random() * emojis.length)];
    ctx.reply(`${randomEmoji} Фырк! Случайный лис призван.`);
});

// --- ОБРАБОТКА ТЕКСТА (Ollama ИЛИ Тодд Говард) ---
bot.on('text', async (ctx) => {
    const userId = ctx.from.id;
    const userText = ctx.message.text;
    const leveledUp = addXp(userId, 5); // Даем +5 XP за текстовую активность

    let aiResponse = "";

    // Пытаемся достучаться до Олламы (как в оригинальном plyt)
    try {
        const response = await axios.post(OLLAMA_URL, {
            model: "liska-1.5", // Название твоей модели
            prompt: userText,
            stream: false
        }, { timeout: 3000 }); // Таймаут 3 секунды, чтобы бот не зависал, если Оллама выключена

        aiResponse = response.data.response;
    } catch (error) {
        // Если Ollama выключена или недоступна в облаке — отвечает Тодд
        aiResponse = `🕶️: ${toddQuotes[Math.floor(Math.random() * toddQuotes.length)]}`;
    }

    if (leveledUp) {
        const user = getUserData(userId);
        aiResponse += `\n\n🎉 Новый уровень: ${user.level}!`;
    }

    ctx.reply(aiResponse);
});

// Старт серверов
app.listen(PORT, () => {
    console.log(`Web server listening on port ${PORT}`);
    bot.launch().then(() => console.log('JS Todd-Plyt Bot is running!'));
});

process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));
