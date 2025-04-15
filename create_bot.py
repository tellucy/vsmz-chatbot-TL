import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from handlers import start_router, feedback_router

def init_bot():
    bot_token = "BOT_TOKEN"
    if not bot_token:
        raise ValueError("Не указан BOT_TOKEN в переменных окружения")
    
    bot = Bot(
        token=bot_token,
        default=DefaultBotProperties(parse_mode='HTML')
    )
    
    dp = Dispatcher(storage=MemoryStorage())
    
    async def set_commands():
        commands = [
            BotCommand(command="start", description="Начать опрос"),
            BotCommand(command="help", description="Помощь")
        ]
        await bot.set_my_commands(commands)
    
    # Регистрация обработчиков
    dp.include_router(start_router)
    dp.include_router(feedback_router)
    
    # Регистрация функции установки команд при старте
    dp.startup.register(set_commands)
    
    return bot, dp