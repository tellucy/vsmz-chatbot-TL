import os
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage
from aioredis import Redis
from aiogram.types import BotCommand
from handlers import start_router, feedback_router
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_bot():
    # Load environment variables
    load_dotenv()
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise ValueError("Не указан BOT_TOKEN в переменных окружения")

    # Initialize bot
    bot = Bot(
        token=bot_token,
        default=DefaultBotProperties(parse_mode='HTML')
    )

    # Connect to Redis
    try:
        redis = Redis(host="localhost", port=6379, decode_responses=True)
        dp = Dispatcher(storage=RedisStorage(redis))
    except Exception as e:
        logger.error(f"Ошибка подключения к Redis: {e}")
        raise

    # Set bot commands
    async def set_commands():
        commands = [
            BotCommand(command="start", description="Начать опрос"),
            BotCommand(command="help", description="Помощь")
        ]
        await bot.set_my_commands(commands)

    # Register handlers
    dp.include_router(start_router)
    dp.include_router(feedback_router)

    # Register startup tasks
    dp.startup.register(set_commands)

    return bot, dp, redis
