<h1 align="center">Plyt</h1>
<p align="center">Мультимодальный бот для модерирования чатов и личного пользования</p>

<div align="center">
<img src="https://img.shields.io/badge/MIT-green?style=for-the-badge"/>
<img src="https://img.shields.io/badge/JavaScript-323330?style=for-the-badge&logo=javascript&logoColor=F7DF1E"/>
<img src="https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge"/>
</div>

## Особенности
- <b>Полная модальность</b>
<br/>Отдельные группы функций можно безболезненно включать и выключать
- <b>Анкеты в чат</b>
<br/>Администраторы могут включить принятие анкет - тогда те, кто захочет попасть в чат, должны будут написать анкету, а участники чата голосуют - за/против вступления
- <b>Модерация чата</b>
<br/>В специальном режиме проверяет фотографии (и в планах - проверка видео) на наличие 18+ контента
- <b>Общение с ИИ</b>
<br/>Если обратиться по имени - делает запрос к [Ollama](https://ollama.com/). Бот также запоминает последние сообщения
- <b>Уровни:</b>
<br/>Для интереса, отправка сообщений, видео и голосовых дает разное количество опыта

## Использование
1. Создать файл ```.env``` и указать ```TELEGRAM_TOKEN```

2. Запустить Docker Compose и установить модель (последнее опционально)
```bash
$ sudo docker compose up
$ sudo docker exec ollama ollama pull gemma2:9b

npm install openai
```

## Разработка
В папке ```src/_``` находятся все модули. Модуль должен наследоваться от ```module.js``` — он содержит потенциальные обработчики событий для прикрепления к экземпляру Telegraf.

Пример кода для запроса к Ollama (запрос на английском языке, как правило, обрабатывается в 2 раза точнее и быстрее)
```import OpenAI from 'openai';

const openai = new OpenAI({
  baseURL: 'https://openrouter.ai/api/v1',
  apiKey: process.env.OPENROUTER_API_KEY, // ключ sk-or-v1-...
});

async function askAI(userMessage) {
  const completion = await openai.chat.completions.create({
    model: 'openrouter/free', // использует любую доступную бесплатную модель
    messages: [
      {
        role: 'system',
        content: 'Ты — лис. Отвечай коротко, дружелюбно и мило, используй :р',
      },
      {
        role: 'user',
        content: userMessage,
      },
    ],
  });

  return completion.choices[0].message.content;
}
```
При замене модели на [новую](https://ollama.com/search) рекомендую заменить её во всех модулях с Ollama: ```ai-trainer.js```, ```ai-talker.js```, а также Dockerfile.ollama

> В последнем обновлении с Docker Compose отключены ```ai-filter.js``` и и ```ai-trainer.js```. Нужно дополнить ```docker-compose.yml``` необходимыми Python скриптами с FastAPI

## Ресурсы
- [Telegraf](https://www.npmjs.com/package/telegraf)
- [Ollama](https://ollama.com/)
- [alpine/ollama](https://github.com/alpine-docker/ollama)

## В планах
- Добавить Python-модули в Docker
- Улучшения тренера языков (или вынести в отдельный проект)
- Админка со статистикой
