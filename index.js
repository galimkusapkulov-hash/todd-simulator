const { Telegraf } = require('telegraf');
const express = require('express');
const axios = require('axios');

// Берем токены из переменных окружения Render
const BOT_TOKEN = process.env.BOT_TOKEN;
const GROQ_API_KEY = process.env.GROQ_API_KEY;

const bot = new Telegraf(BOT_TOKEN);
const app = express();
const PORT = process.env.PORT || 8080;

app.get('/', (req, res) => {
    res.send('It just works! Cloud AI Engine Live.');
});

// --- БАЗА ДАННЫХ В ПАМЯТИ ---
const db = {};

function getUserData(userId) {
    if (!db[userId]) {
        db[userId] = { level: 1, xp: 0, fox: { satiety: 50, mood: 50, energy: 50 } };
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
        return true;
    }
    return false;
}

// --- КОМАНДЫ БОТА ---
bot.start((ctx) => {
    ctx.replyWithMarkdown(
        "🕶️ *Система Plyt Cloud AI активирована!*\n\n" +
        "Уровни, опыт и тамагочи-команды работают 24/7. Теперь я подключен к мощному ИИ разуму.\n\n" +
        "Пиши мне что угодно, я отвечу как надо!"
    );
});

bot.command('status', (ctx) => {
    const user = getUserData(ctx.from.id);
    ctx.replyWithMarkdown(
        `📊 *Твой профиль:*\n` +
        `⭐ Уровень: ${user.level}\n` +
        `✨ Опыт (XP): ${user.xp}/${user.level * 100}\n\n` +
        `🍖 Сытость лиса: ${user.fox.satiety}/100\n` +
        `🦊 Настроение лиса: ${user.fox.mood}/100\n` +
        `⚡ Энергия лиса: ${user.fox.energy}/100`
    );
});

bot.command('feed', (ctx) => {
    const user = getUserData(ctx.from.id);
    user.fox.satiety = Math.min(100, user.fox.satiety + 20);
    addXp(ctx.from.id, 15);
    ctx.reply("🍖 Вы покормили Лиса! Сытость повышена, получено +15 XP.");
});

bot.command('hug', (ctx) => {
    const user = getUserData(ctx.from.id);
    user.fox.mood = Math.min(100, user.fox.mood + 20);
    addXp(ctx.from.id, 10);
    ctx.reply("🦊 Вы обняли Лиса! Он довольно фыркает. Получено +10 XP.");
});

bot.command('play', (ctx) => {
    const user = getUserData(ctx.from.id);
    if (user.fox.energy < 20) return ctx.reply("⚡ Лис устал, отправь его спать через /sleep");
    user.fox.mood = Math.min(100, user.fox.mood + 15);
    user.fox.energy = Math.max(0, user.fox.energy - 20);
    const leveledUp = addXp(ctx.from.id, 25);
    ctx.reply(`🎮 Поиграли с Лисом! Получено +25 XP.${leveledUp ? `\n\n🎉 УРОВЕНЬ ПОВЫШЕН! Теперь у тебя ${user.level} лвл!` : ''}`);
});

bot.command('sleep', (ctx) => {
    const user = getUserData(ctx.from.id);
    user.fox.energy = Math.min(100, user.fox.energy + 40);
    ctx.reply("💤 Лис ушел спать. Энергия восстановлена.");
});

bot.command('fox', (ctx) => {
    const emojis = ["🦊", "🦊🐾", "🦊✨", "🐺"];
    ctx.reply(`${emojis[Math.floor(Math.random() * emojis.length)]} Фырк! Призван случайный лис.`);
});

// --- ИНТЕГРАЦИЯ С ОБЛАЧНЫМ GROQ AI ---
bot.on('text', async (ctx) => {
    const userId = ctx.from.id;
    const userText = ctx.message.text;
    const leveledUp = addXp(userId, 5); // +5 XP за сообщение

    if (!GROQ_API_KEY) {
        return ctx.reply("🕶️: Ошибка! Забыл добавить GROQ_API_KEY в переменные окружения Render.");
    }

    try {
        const response = await axios.post(
            'https://api.groq.com/openai/v1/chat/completions',
            {
                model: 'llama3-8b-8192', // Быстрая и умная модель
                messages: [
                    {
                        role: 'system',
                        content: 'Ты — уникальный гибрид хитрого серого лиса-фурри и Тодда Говарда. Ты общаешься в чате с другом. Твой стиль речи: немного саркастичный, ироничный, уверенный в себе, используешь сленг, иногда упоминаешь, что "всё просто работает" (it just works) или предлагаешь купить Скайрим. Пиши коротко, живо, не пиши банальные ИИ-ответы, общайся как реальный бро.'
                    },
                    { role: 'user', content: userText }
                ],
                max_tokens: 150
            },
            {
                headers: {
                    'Authorization': `Bearer ${GROQ_API_KEY}`,
                    'Content-Type': 'application/json'
                }
            }
        );

        let aiResponse = response.data.choices[0].message.content;

        if (leveledUp) {
            const user = getUserData(userId);
            aiResponse += `\n\n🎉 Новый уровень: ${user.level}!`;
        }

        ctx.reply(aiResponse);

    } catch (error) {
        console.error(error);
        ctx.reply("🕶️: Что-то движок Creation Engine сбоит, повтори еще раз.");
    }
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
    bot.launch();
});
