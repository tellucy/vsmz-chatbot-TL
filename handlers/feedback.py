from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from handlers.states import FeedbackStates
import json

feedback_router = Router()

def save_to_json(data: dict):
    """Saves survey data to a JSON file."""
    try:
        with open('feedback.json', 'a', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
            f.write('\n')
    except Exception as e:
        print(f"Error saving data: {e}")

@feedback_router.message(lambda msg: msg.text == "Начать опрос")
async def start_survey(message: Message, state: FSMContext):
    """Starts the survey."""
    # Send the initial message
    await message.answer("Опрос начат! Пожалуйста, ответьте на вопросы.")
    
    # Transition to the 'gender' state
    builder = ReplyKeyboardBuilder()
    for gender in ["Мужской", "Женский", "Предпочитаю не указывать"]:
        builder.add(types.KeyboardButton(text=gender))
    builder.adjust(2)
    
    await message.answer(
        "Укажите ваш пол:",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )
    await state.set_state(FeedbackStates.gender)

@feedback_router.message(FeedbackStates.gender)
async def process_gender(message: Message, state: FSMContext):
    """Processes gender input."""
    if message.text not in ["Мужской", "Женский", "Предпочитаю не указывать"]:
        await message.answer("Пожалуйста, выберите вариант из кнопок ниже.")
        return
    
    await state.update_data(gender=message.text)
    await message.answer("Укажите ваш возраст:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(FeedbackStates.age)

@feedback_router.message(FeedbackStates.age)
async def process_age(message: Message, state: FSMContext):
    """Processes age input."""
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите возраст числом.")
        return
    
    age = int(message.text)
    if not 1 <= age <= 120:
        await message.answer("Введите реальный возраст (1-120).")
        return
    
    await state.update_data(age=age)
    await message.answer("Из какого вы города?")
    await state.set_state(FeedbackStates.home_city)

@feedback_router.message(FeedbackStates.home_city)
async def process_home_city(message: Message, state: FSMContext):
    """Processes home city input."""
    if len(message.text) < 2:
        await message.answer("Название города слишком короткое.")
        return
    
    await state.update_data(home_city=message.text)
    await message.answer("Какой город вы посетили?")
    await state.set_state(FeedbackStates.visited_city)

@feedback_router.message(FeedbackStates.visited_city)
async def process_visited_city(message: Message, state: FSMContext):
    """Processes visited city input."""
    await state.update_data(visited_city=message.text)
    await message.answer("Что именно вы посетили?")
    await state.set_state(FeedbackStates.visited_events)

@feedback_router.message(FeedbackStates.visited_events)
async def process_visited_events(message: Message, state: FSMContext):
    """Processes visited events input."""
    await state.update_data(visited_events=message.text)
    await message.answer("Что вам понравилось больше всего?")
    await state.set_state(FeedbackStates.liked)

@feedback_router.message(FeedbackStates.liked)
async def process_liked(message: Message, state: FSMContext):
    """Processes liked aspects input."""
    await state.update_data(liked=message.text)
    await message.answer("Что вам не понравилось или что можно улучшить?")
    await state.set_state(FeedbackStates.disliked)

@feedback_router.message(FeedbackStates.disliked)
async def process_disliked(message: Message, state: FSMContext):
    """Processes disliked aspects and ends the survey."""
    await state.update_data(disliked=message.text)
    user_data = await state.get_data()
    save_to_json(user_data)
    
    await message.answer(
        "Спасибо за ваши ответы! Ваше мнение очень важно для нас.",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()