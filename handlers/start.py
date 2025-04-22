from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

start_router = Router()

@start_router.message(CommandStart())
async def cmd_start(message: Message):
    """Handles the /start command."""
    builder = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Начать опрос")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    welcome_text = (
        "Здравствуйте! Спасибо за посещение Государственного Владимиро-Суздальского "
        "музея-заповедника. Мы хотим узнать ваше мнение, чтобы стать лучше."
    )
    
    await message.answer(welcome_text, reply_markup=builder)