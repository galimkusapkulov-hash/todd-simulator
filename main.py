const { Telegraf } = require('telegraf');
const express = require('express');

// Токен берем из переменных окружения
const BOT_TOKEN = process.env.BOT_TOKEN || "8415425477:AAEo6qnbFQfGMF_A7ugA0Ozz7eXdUTN6k98";
const bot = new Telegraf(BOT_TOKEN);

// Инициализируем Express для веб-сервера (чтобы Render не спал)
const app = express();
const PORT = process.env.PORT || 8080;

app.get('/', (req, res) => {
    res.send('It just works! (Todd Engine JS v1.5)');
});

// --- БАЗА ДАННЫХ (в памяти) ---
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
        return true; // Апнулся уровень
    }
    return false;
}

// Цитаты Тодда Говарда
const toddQuotes = [
    "Слышь, купи Скайрим. Там теперь можно грабить корованы, и он идет на твоем тостере.",
    "В нашей новой игре будет 16-кратно увеличенная детализация. Вы сможете зайти в каждое здание!",
    "Видите ту гору? Вы можете на неё взойти. Это не декорация.",
    "Она просто работает (It just works). Если вы видите баг — это не баг, это неожиданная геймплейная фича.",
    "Мы переиздаем TES V: Skyrim на умные холодильники. Предзаказ уже открыт."
];

// --- ХЭНДЛЕРЫ КОМАНД ---

bot.start((ctx) => {
    ctx.replyWithMarkdown(
        "🕶️ *Тодд Говард и Лис приветствуют тебя!*\n\n" +
        "Мы перенесли весь движок `plyt` на JS. Системы уровней, опыта и тамагочи активированы. **Оно просто работает.**\n\n" +
        "Используй меню, чтобы прокачиваться и следить за Лисом!"
    );
});

bot.command('status', (ctx) => {
    const user = getUserData(ctx.from.id);
    ctx.replyWithMarkdown(
        `📊 *Твой профиль (модуль Levels & Fox):*\n` +
        `⭐ Уровень: ${user.level}\n` +
        `✨ Опыт (XP): ${user.xp}/${user.level * 100}\n\n` +
        `🍖 Сытость лиса: ${user.fox.satiety}/100\n` +
        `🦊 Настроение лиса: ${user.fox.mood}/100\n` +
        `⚡ Энергия лиса: ${user.fox.energy}/100\n\n` +
        `🕶️ _«16-кратная детализация твоего прогресса!»_`
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
    ctx.reply("🦊 Вы обняли Лиса! Он довольно фыркает. Получено +10 XP.");
});

bot.command('play', (ctx) => {
    const user = getUserData(ctx.from.id);
    if (user.fox.energy < 20) {
        return ctx.reply("⚡ Лис без сил. Ему нужно поспать (/sleep) перед игрой в Скайрим.");
    }
    user.fox.mood = Math.min(100, user.fox.mood + 15);
    user.fox.energy = Math.max(0, user.fox.energy - 20);
    const leveledUp = addXp(ctx.from.id, 25);
    
    let text = "🎮 Вы поиграли с Лисом! Настроение выросло, получено +25 XP.";
    if (leveledUp) text += `\n\n🎉 УРОВЕНЬ ПОВЫШЕН! Теперь у тебя ${user.level} уровень!`;
    ctx.reply(text);
});

bot.command('sleep', (ctx) => {
    const user = getUserData(ctx.from.id);
    user.fox.energy = Math.min(100, user.fox.energy + 40);
    ctx.reply("💤 Лис свернулся клубком и спит. Энергия восстановлена.");
});

bot.command('fox', (ctx) => {
    const emojis = ["🦊", "🦊🐾", "🦊✨", "🐺"];
    const randomEmoji = emojis[Math.floor(Math.random() * emojis.length)];
    ctx.reply(`${randomEmoji} Фырк! Вы призвали случайного лиса.`);
});

// Ответы Тодда на обычные сообщения + начисление опыта за текстовую активность
bot.on('text', (ctx) => {
    const leveledUp = addXp(ctx.from.id, 5); // +5 XP за сообщение
    const quote = toddQuotes[Math.floor(Math.random() * toddQuotes.length)];
    
    let replyText = `🕶️: ${quote}`;
    if (leveledUp) {
        const user = getUserData(ctx.from.id);
        replyText += `\n\n🎉 Новый уровень: ${user.level}!`;
    }
    ctx.reply(replyText);
});

// Запуск бота и веб-сервера
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
    bot.launch().then(() => console.log('Todd Bot is Live!'));
});

// Мягкая остановка
process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));
