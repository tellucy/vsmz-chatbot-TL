import asyncio
import json
import aiogram
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
import logging
logging.basicConfig(level=logging.INFO)

class FeedbackStates(StatesGroup):
    gender = State()
    age = State()
    home_city = State()
    visited_city = State()
    visited_events = State()
    liked = State()
    disliked = State()

class TranslationState(StatesGroup):
    waiting_for_text = State()

# Словарь для перевода кириллицы в глаголицу
GLAGOLITIC_MAP = {
    'а': 'Ⰰ', 'б': 'Ⰱ', 'в': 'Ⰲ', 'г': 'Ⰳ', 'д': 'Ⰴ',
    'е': 'Ⰵ', 'ё': 'Ⰵ', 'ж': 'Ⰶ', 'з': 'Ⰷ', 'и': 'Ⰻ', 'й': 'Ⰼ',
    'к': 'Ⰽ', 'л': 'Ⰾ', 'м': 'Ⰿ', 'н': 'Ⱀ', 'о': 'Ⱁ',
    'п': 'Ⱂ', 'р': 'Ⱃ', 'с': 'Ⱄ', 'т': 'Ⱅ', 'у': 'Ⱆ',
    'ф': 'Ⱇ', 'х': 'Ⱈ', 'ц': 'Ⱌ', 'ч': 'Ⱍ', 'ш': 'Ⱎ',
    'щ': 'Ⱋ', 'ъ': 'Ⱏ', 'ы': 'Ⰺ', 'ь': 'Ⱐ', 'ѣ': 'Ⱑ',
    'э': 'Ⰵ', 'ю': 'Ⱓ', 'я': 'Ⱔ',
    'А': 'Ⰰ', 'Б': 'Ⰱ', 'В': 'Ⰲ', 'Г': 'Ⰳ', 'Д': 'Ⰴ',
    'Е': 'Ⰵ', 'Ё': 'Ⰵ', 'Ж': 'Ⰶ', 'З': 'Ⰷ', 'И': 'Ⰻ', 'Й': 'Ⰼ',
    'К': 'Ⰽ', 'Л': 'Ⰾ', 'М': 'Ⰿ', 'Н': 'Ⱀ', 'О': 'Ⱁ',
    'П': 'Ⱂ', 'Р': 'Ⱃ', 'С': 'Ⱄ', 'Т': 'Ⱅ', 'У': 'Ⱆ',
    'Ф': 'Ⱇ', 'Х': 'Ⱈ', 'Ц': 'Ⱌ', 'Ч': 'Ⱍ', 'Ш': 'Ⱎ',
    'Щ': 'Ⱋ', 'Ъ': 'Ⱏ', 'Ы': 'Ⰺ', 'Ь': 'Ⱐ', 'Ѣ': 'Ⱑ',
    'Э': 'Ⰵ', 'Ю': 'Ⱓ', 'Я': 'Ⱔ'
}

load_dotenv()
bot_token = os.getenv("BOT_TOKEN")

bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

def save_to_json(data: dict):
    try:
        with open('feedback.json', 'a', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
            f.write('\n')
    except Exception as e:
        print(f"Error saving data: {e}")

def translate_to_glagolitic(text: str) -> str:
    """Переводит кириллический текст в глаголицу"""
    result = []
    for char in text:
        if char in GLAGOLITIC_MAP:
            result.append(GLAGOLITIC_MAP[char])
        else:
            result.append(char)  # Оставляем эмодзи и другие символы как есть
    return ''.join(result)

@dp.message(F.text == "/start")
async def start_feedback(message: types.Message, state: FSMContext):  # Добавляем параметр state
    await state.clear()  # Теперь state определен
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать опрос"))
    builder.add(types.KeyboardButton(text="Перевод на глаголицу"))

    await message.answer(
        "Здравствуйте! Спасибо за посещение музея. Нажмите кнопку, чтобы начать опрос.",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )

@dp.message(F.text == "Начать опрос")
async def start_survey(message: types.Message, state: FSMContext):
    await state.set_state(FeedbackStates.gender)
    builder = ReplyKeyboardBuilder()
    for gender in ["Мужской", "Женский", "Предпочитаю не указывать"]:
        builder.add(types.KeyboardButton(text=gender))
    builder.adjust(2)

    await message.answer(
        "Укажите ваш пол:",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )
    await state.set_state(FeedbackStates.gender)

@dp.message(F.text == "Перевод на глаголицу")
async def start_glagolitic_translation(message: types.Message, state: FSMContext):
    await state.set_state(TranslationState.waiting_for_text)
    await message.answer(
        "Введите текст на кириллице для перевода в глаголицу:",
        reply_markup=types.ReplyKeyboardRemove()
    )

@dp.message(F.text == "Перевести ещё")
async def translate_more(message: types.Message, state: FSMContext):
    await start_glagolitic_translation(message, state)

@dp.message(F.text == "Перейти к опросу")
async def switch_to_survey(message: types.Message, state: FSMContext):
    await start_survey(message, state)

@dp.message(TranslationState.waiting_for_text)
async def handle_glagolitic_translation(message: types.Message, state: FSMContext):
    # Проверяем, что текст содержит хотя бы одну кириллическую букву
    if any(char in GLAGOLITIC_MAP for char in message.text):
        translated = translate_to_glagolitic(message.text)
        
        builder = ReplyKeyboardBuilder()
        builder.add(types.KeyboardButton(text="Перевести ещё"))
        builder.add(types.KeyboardButton(text="Перейти к опросу"))
        
        await message.answer(
            f"Перевод на глаголицу:\n\n{translated}",
            reply_markup=builder.as_markup(resize_keyboard=True)
        )
    else:
        await message.answer("Пожалуйста, введите текст, содержащий кириллические символы.")

@dp.message(FeedbackStates.gender)
async def process_gender(message: types.Message, state: FSMContext):
    if message.text not in ["Мужской", "Женский", "Предпочитаю не указывать"]:
        await message.answer("Пожалуйста, выберите вариант из кнопок ниже")
        return

    await state.update_data(gender=message.text)
    await message.answer(
        "Укажите ваш возраст:",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(FeedbackStates.age)

@dp.message(FeedbackStates.age)
async def process_age(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите возраст числом:")
        return

    age = int(message.text)
    if not 1 <= age <= 120:
        await message.answer("Введите реальный возраст (1-120):")
        return

    await state.update_data(age=age)
    await message.answer("Из какого вы города?")
    await state.set_state(FeedbackStates.home_city)

@dp.message(FeedbackStates.home_city)
async def process_home_city(message: types.Message, state: FSMContext):
    if len(message.text) < 2:
        await message.answer("Название города слишком короткое")
        return

    await state.update_data(home_city=message.text)

    builder = ReplyKeyboardBuilder()
    cities = ["Владимир", "Суздаль", "Гусь-Хрустальный",
             "с. Муромцево", "пос. Боголюбово", "Юрьев-Польский"]
    for city in cities:
        builder.add(types.KeyboardButton(text=city))
    builder.adjust(2)
    builder.add(types.KeyboardButton(text="Другое"))

    await message.answer(
        "Какой город вы посетили?",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )
    await state.set_state(FeedbackStates.visited_city)

@dp.message(FeedbackStates.visited_city)
async def process_visited_city(message: types.Message, state: FSMContext):
    await state.update_data(visited_city=message.text)
    await message.answer(
        "Что именно вы посетили? (экспозицию/выставку/экскурсию/мероприятие)",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(FeedbackStates.visited_events)

@dp.message(FeedbackStates.visited_events)
async def process_visited_events(message: types.Message, state: FSMContext):
    if len(message.text) < 5:
        await message.answer("Пожалуйста, напишите более подробно")
        return

    await state.update_data(visited_events=message.text)
    await message.answer("Что вам понравилось больше всего?")
    await state.set_state(FeedbackStates.liked)

@dp.message(FeedbackStates.liked)
async def process_liked(message: types.Message, state: FSMContext):
    if len(message.text) < 5:
        await message.answer("Пожалуйста, напишите более развернуто")
        return

    await state.update_data(liked=message.text)
    await message.answer("Что вам не понравилось или что можно улучшить?")
    await state.set_state(FeedbackStates.disliked)

@dp.message(FeedbackStates.disliked)
async def process_disliked(message: types.Message, state: FSMContext):
    await state.update_data(disliked=message.text)
    user_data = await state.get_data()

    save_to_json(user_data)

    await message.answer(
        "Спасибо за обратную связь! Мы учтем ваши замечания.",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.clear()

# ================= ЗАПУСК БОТА =================
async def main():
    while True:
        try:
            logging.info("Запуск бота...")
            await dp.start_polling(bot)
        except Exception as e:
            logging.error(f"Ошибка: {e}. Перезапуск через 10 секунд...")
            await asyncio.sleep(10)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
