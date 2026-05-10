"""Telegram bots implementation

Two bots are created:
- Trainer bot (name "раб") – generates a program/code based on the user's request using the Anthropic model via OpenRouter.
- Simple chat bot (name "шегол") – replies to messages using the same model for casual conversation.

Both bots share the same runtime and load credentials from a .env file that is ignored by git.
"""

import os
import logging
import asyncio
from pathlib import Path

from dotenv import load_dotenv
import requests
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Load environment variables (ignored by git)
load_dotenv()

# Tokens for the two bots
TOKEN_RAB = os.getenv("TELEGRAM_TOKEN_RAB")
TOKEN_SHAGOL = os.getenv("TELEGRAM_TOKEN_SHAGOL")

# Anthropic/OpenRouter configuration
ANTHROPIC_BASE_URL = os.getenv("ANTHROPIC_BASE_URL")
ANTHROPIC_AUTH_TOKEN = os.getenv("ANTHROPIC_AUTH_TOKEN")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "openai/gpt-oss-120b")

if not all([TOKEN_RAB, TOKEN_SHAGOL, ANTHROPIC_BASE_URL, ANTHROPIC_AUTH_TOKEN]):
    raise RuntimeError("Missing required environment variables")

# Simple logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def anthropic_chat(prompt: str) -> str:
    """Send a prompt to the Anthropic model via OpenRouter and return the response text."""
    headers = {
        "Authorization": f"Bearer {ANTHROPIC_AUTH_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": ANTHROPIC_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1024,
    }
    response = requests.post(ANTHROPIC_BASE_URL, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    data = response.json()
    # OpenRouter returns a list of choices; we take the first message content
    return data.get("choices", [{}])[0].get("message", {}).get("content", "")


# ----- Trainer bot ("раб") -----
async def rab_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Привет! Я бот‑тренер \"раб\". Опиши задачу, и я составлю для тебя программу."
    )

async def rab_handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_prompt = update.message.text
    # Build a request asking the model to generate a full program
    prompt = (
        f"Ты бот‑тренер. Пользователь просит написать программу по следующему запросу:\n\n"
        f"{user_prompt}\n\n"
        "Сгенерируй полностью готовый исходный код на любом языке, который подходит для задачи, "
        "и включи комментарии на русском, поясняя ключевые части."
    )
    try:
        response = anthropic_chat(prompt)
        await update.message.reply_text(response)
    except Exception as e:
        logger.exception("Error calling Anthropic API")
        await update.message.reply_text("Произошла ошибка при генерации кода.")

# ----- Simple chat bot ("шегол") -----
async def shagol_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Привет! Я бот‑чат \"шегол\". Пиши, будем болтать."
    )

async def shagol_handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_prompt = update.message.text
    prompt = f"Веди дружелюбный разговор на русском, отвечай кратко. Пользователь написал: {user_prompt}"
    try:
        response = anthropic_chat(prompt)
        await update.message.reply_text(response)
    except Exception as e:
        logger.exception("Error calling Anthropic API")
        await update.message.reply_text("Ошибка при получении ответа.")


async def main() -> None:
    # Build two separate applications, each with its own token
    app_rab = ApplicationBuilder().token(TOKEN_RAB).build()
    app_shagol = ApplicationBuilder().token(TOKEN_SHAGOL).build()

    # Register handlers for trainer bot
    app_rab.add_handler(CommandHandler("start", rab_start))
    app_rab.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, rab_handle_message))

    # Register handlers for chat bot
    app_shagol.add_handler(CommandHandler("start", shagol_start))
    app_shagol.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, shagol_handle_message))

    # Run both bots concurrently
    await asyncio.gather(app_rab.run_polling(), app_shagol.run_polling())


if __name__ == "__main__":
    asyncio.run(main())
