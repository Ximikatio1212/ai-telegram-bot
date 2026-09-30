# 🚀 Деплой на Render

## Пошаговая инструкция

### Шаг 1: Создай репозиторий на GitHub
1. Зайди на https://github.com
2. Нажми **"New repository"**
3. Название: `ai-telegram-bot`
4. Нажми **"Create repository"**

### Шаг 2: Загрузи файлы
1. На странице репозитория нажми **"uploading an existing file"**
2. Перетащи все файлы из папки проекта:
   - `bot.py`
   - `config.py`
   - `requirements.txt`
   - `render.yaml`
   - `Dockerfile`
   - папка `modules/`
3. Нажми **"Commit changes"**

### Шаг 3: Регистрация на Render
1. Зайди на https://render.com
2. Нажми **"Get Started"** → выбери **"GitHub"**
3. Авторизуйся через GitHub
4. Разреши доступ к репозиториям

### Шаг 4: Создание сервиса
1. Нажми **"New +"** → **"Web Service"**
2. Выбери репозиторий `ai-telegram-bot`
3. Нажми **"Connect"**

### Шаг 5: Настройка
- **Name:** `ai-telegram-bot`
- **Runtime:** Python 3
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python bot.py`
- **Plan:** Free

### Шаг 6: Переменные окружения
Нажми **"Environment"** и добавь:

| Key | Value |
|-----|-------|
| `BOT_TOKEN` | `8275482287:AAEO9YvDNd8Tc94UAthO7w8193ABog-Dc40` |
| `GEMINI_API_KEY` | `AQ.Ab8RN6J_BZkjjI8W5-e6BUFgvV46rngEryETviVGTrSoJIAiIw` |
| `API_ID` | `32146160` |
| `API_HASH` | `ae96a4fa8b6c045b6c79c4f5b15ceb34` |

### Шаг 7: Деплой
1. Нажми **"Create Web Service"**
2. Подожди 2-3 минуты
3. Готово! 🎉

---

## Проверка

После деплоя:
1. Открой бота в Telegram
2. Напиши `/start`
3. Проверь: `/ask привет`

---

## Проблемы

**Бот не запускается**
→ Проверь логи в панели Render (вкладка "Logs")

**Ошибка "429"**
→ Лимит Gemini, подожди минуту

**Бот не отвечает**
→ Проверь, что переменные окружения заданы правильно
