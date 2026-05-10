# Telegram AI Bot с двумя агентами

Telegram бот с двумя AI агентами на базе Claude API:
- **🔧 Разработчик** - пишет код на любом языке программирования
- **💡 Советник** - дает советы и рекомендации

## Возможности

- Два специализированных AI агента с разными навыками
- История разговоров сохраняется для каждого агента отдельно
- Контекст разговора передается в Claude API
- База данных SQLite для хранения истории

## Локальная установка

### 1. Клонируйте репозиторий
```bash
git clone https://github.com/Daniyar0612/telegram-ai-bot.git
cd telegram-ai-bot
```

### 2. Установите зависимости
```bash
pip install -r requirements.txt
```

### 3. Настройте переменные окружения

Создайте файл `.env` на основе `.env.example`:
```bash
cp .env.example .env
```

Заполните `.env` файл:
```env
TELEGRAM_BOT_TOKEN=ваш_токен_от_BotFather
ANTHROPIC_API_KEY=ваш_ключ_от_Anthropic
```

**Где получить токены:**
- **Telegram Bot Token**: напишите [@BotFather](https://t.me/BotFather) в Telegram, создайте бота командой `/newbot`
- **Anthropic API Key**: зарегистрируйтесь на [console.anthropic.com](https://console.anthropic.com/)

### 4. Запустите бота
```bash
python main.py
```

## Деплой на Fly.io (бот работает 24/7)

Fly.io - бесплатный хостинг для вашего бота.

### Шаг 1: Установка Fly CLI

**Windows:**
```powershell
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

**Mac/Linux:**
```bash
curl -L https://fly.io/install.sh | sh
```

### Шаг 2: Авторизация

```bash
fly auth login
```

### Шаг 3: Создание приложения

```bash
cd telegram-ai-bot
fly launch --no-deploy
```

Fly CLI спросит:
- **App name**: оставьте предложенное или введите свое
- **Region**: выберите ближайший регион (например, Amsterdam)
- **PostgreSQL**: выберите **No** (используем SQLite)
- **Redis**: выберите **No**

### Шаг 4: Настройка переменных окружения

```bash
fly secrets set TELEGRAM_BOT_TOKEN="ваш_токен_от_BotFather"
fly secrets set ANTHROPIC_API_KEY="ваш_ключ_от_Anthropic"
```

### Шаг 5: Деплой

```bash
fly deploy
```

**Готово!** Ваш бот теперь работает 24/7 ✅

### Полезные команды

```bash
fly logs              # Смотреть логи бота
fly status            # Проверить статус
fly ssh console       # Подключиться к контейнеру
fly apps restart      # Перезапустить бота
```

### Мониторинг

В [Fly.io Dashboard](https://fly.io/dashboard) вы можете:
- Смотреть метрики и логи
- Управлять приложением
- Отслеживать использование ресурсов

## Использование бота

### Команды

- `/start` - начать работу с ботом
- `/developer` - переключиться на агента-разработчика
- `/advisor` - переключиться на агента-советника
- `/clear` - очистить историю текущего разговора
- `/help` - показать справку

### Примеры использования

**Разработчик:**
```
Пользователь: Напиши функцию на Python для сортировки списка
Разработчик: [предоставит код с объяснениями]
```

**Советник:**
```
Пользователь: Как лучше организовать свое время?
Советник: [даст практические советы и рекомендации]
```

## Структура проекта

```
telegram-ai-bot/
├── main.py           # Основной код бота
├── config.py         # Конфигурация агентов
├── database.py       # Работа с SQLite
├── requirements.txt  # Зависимости Python
├── Dockerfile        # Docker образ для Fly.io
├── fly.toml          # Конфигурация Fly.io
├── .dockerignore     # Игнорируемые файлы для Docker
├── .env.example      # Шаблон для переменных окружения
└── .gitignore        # Игнорируемые файлы
```

## Технологии

- **Python 3.11**
- **python-telegram-bot** - библиотека для Telegram Bot API
- **Anthropic Claude API** - AI модель для агентов
- **SQLite** - база данных для истории
- **Fly.io** - хостинг для 24/7 работы
- **Docker** - контейнеризация приложения

## Безопасность

⚠️ **Важно:**
- Никогда не коммитьте `.env` файл в Git
- `.env` уже добавлен в `.gitignore`
- На Fly.io используйте `fly secrets` для переменных окружения
- Регулярно ротируйте API ключи
- Установите лимиты расходов в Anthropic Console

## Лицензия

MIT License - используйте свободно!

## Поддержка

Если возникли вопросы или проблемы, создайте [Issue](https://github.com/Daniyar0612/telegram-ai-bot/issues) в репозитории.
