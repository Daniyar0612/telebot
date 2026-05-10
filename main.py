"""
Telegram бот с двумя AI агентами на базе Google Gemini API
"""
import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai
from database import Database
from config import AGENTS, MAX_HISTORY_MESSAGES

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
    raise ValueError("Не найдены TELEGRAM_BOT_TOKEN или GEMINI_API_KEY в .env файле")

# Настройка Gemini API
genai.configure(api_key=GEMINI_API_KEY)
db = Database()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user_id = update.effective_user.id

    welcome_message = """
👋 Привет! Я AI бот с двумя агентами:

🔧 *Разработчик* - помогает писать код на любом языке программирования
💡 *Советник* - дает советы и рекомендации по любым вопросам

Выберите агента:
/developer - переключиться на разработчика
/advisor - переключиться на советника

Другие команды:
/clear - очистить историю текущего разговора
/help - показать эту справку
"""

    await update.message.reply_text(welcome_message, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    await start(update, context)


async def developer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Переключиться на агента-разработчика"""
    user_id = update.effective_user.id
    db.set_current_agent(user_id, "developer")

    await update.message.reply_text(
        "🔧 Вы переключились на *Разработчика*\n\n"
        "Я помогу вам написать код на любом языке программирования. "
        "Просто опишите, что вам нужно!",
        parse_mode='Markdown'
    )


async def advisor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Переключиться на агента-советника"""
    user_id = update.effective_user.id
    db.set_current_agent(user_id, "advisor")

    await update.message.reply_text(
        "💡 Вы переключились на *Советника*\n\n"
        "Я помогу вам с советами и рекомендациями. "
        "Расскажите, что вас беспокоит или над чем вы думаете!",
        parse_mode='Markdown'
    )


async def clear_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Очистить историю текущего разговора"""
    user_id = update.effective_user.id
    current_agent = db.get_current_agent(user_id)

    if not current_agent:
        await update.message.reply_text(
            "Сначала выберите агента: /developer или /advisor"
        )
        return

    db.clear_history(user_id, current_agent)
    agent_name = AGENTS[current_agent]["name"]

    await update.message.reply_text(
        f"✅ История разговора с агентом *{agent_name}* очищена",
        parse_mode='Markdown'
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    user_id = update.effective_user.id
    user_message = update.message.text

    # Проверяем, выбран ли агент
    current_agent = db.get_current_agent(user_id)
    if not current_agent:
        await update.message.reply_text(
            "Пожалуйста, сначала выберите агента:\n"
            "/developer - для помощи с кодом\n"
            "/advisor - для советов и рекомендаций"
        )
        return

    # Показываем индикатор печати
    await update.message.chat.send_action("typing")

    try:
        # Сохраняем сообщение пользователя
        db.add_message(user_id, current_agent, "user", user_message)

        # Получаем историю разговора
        history = db.get_history(user_id, current_agent, MAX_HISTORY_MESSAGES)

        # Получаем конфигурацию агента
        agent_config = AGENTS[current_agent]

        # Создаем модель Gemini
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            system_instruction=agent_config["system_prompt"]
        )

        # Формируем историю для Gemini
        chat_history = []
        for msg in history[:-1]:  # Все кроме последнего (текущего) сообщения
            chat_history.append({
                "role": msg["role"],
                "parts": [msg["content"]]
            })

        # Создаем чат с историей
        chat = model.start_chat(history=chat_history)

        # Отправляем текущее сообщение
        response = chat.send_message(user_message)

        # Извлекаем ответ
        assistant_message = response.text

        # Сохраняем ответ ассистента
        db.add_message(user_id, current_agent, "model", assistant_message)

        # Отправляем ответ пользователю
        # Разбиваем длинные сообщения на части (Telegram лимит 4096 символов)
        max_length = 4096
        if len(assistant_message) <= max_length:
            await update.message.reply_text(assistant_message)
        else:
            # Разбиваем на части
            for i in range(0, len(assistant_message), max_length):
                chunk = assistant_message[i:i + max_length]
                await update.message.reply_text(chunk)

    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}")
        await update.message.reply_text(
            "❌ Произошла ошибка при обработке вашего запроса. "
            "Пожалуйста, попробуйте еще раз."
        )


def main():
    """Запуск бота"""
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("developer", developer))
    application.add_handler(CommandHandler("advisor", advisor))
    application.add_handler(CommandHandler("clear", clear_history))

    # Регистрируем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота
    logger.info("Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Бот остановлен")
    finally:
        db.close()
