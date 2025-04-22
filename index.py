import asyncio
import logging
from create_bot import init_bot

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    # Initialize bot, dispatcher, and Redis
    bot, dp, redis = await init_bot()

    try:
        logger.info("Бот запущен. Ожидание сообщений...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
    finally:
        # Gracefully close Redis connection
        await redis.close()
        await redis.connection_pool.disconnect()
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.warning("Бот остановлен вручную.")