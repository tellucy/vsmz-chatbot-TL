from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from handlers.states import FeedbackStates
import json

feedback_router = Router()

def save_to_json(data: dict):
    """Сохранение данных опроса в JSON файл"""
    try:
        with open('feedback.json', 'a', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
            f.write('\n')
    except Exception as e:
        print(f"Error saving data: {e}")

@feedback_router.message(F.text == "Начать опрос")
async def start_survey(message: Message, state: FSMContext):
    """Обработчик начала опроса"""
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
    """Обработчик выбора пола"""
    if message.text not in ["Мужской", "Женский", "Предпочитаю не указывать"]:
        await message.answer("Пожалуйста, выберите вариант из кнопок ниже")
        return
    
    await state.update_data(gender=message.text)
    await message.answer(
        "Укажите ваш возраст:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(FeedbackStates.age)

@feedback_router.message(FeedbackStates.age)
async def process_age(message: Message, state: FSMContext):
    """Обработчик ввода возраста"""
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

@feedback_router.message(FeedbackStates.home_city)
async def process_home_city(message: Message, state: FSMContext):
    """Обработчик ввода города проживания"""
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

@feedback_router.message(FeedbackStates.visited_city)
async def process_visited_city(message: Message, state: FSMContext):
    """Обработчик выбора посещенного города"""
    await state.update_data(visited_city=message.text)
    await message.answer(
        "Что именно вы посетили? (экспозицию/выставку/экскурсию/мероприятие)",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(FeedbackStates.visited_events)

@feedback_router.message(FeedbackStates.visited_events)
async def process_visited_events(message: Message, state: FSMContext):
    """Обработчик ввода посещенных мероприятий"""
    if len(message.text) < 5:
        await message.answer("Пожалуйста, напишите более подробно")
        return
    
    await state.update_data(visited_events=message.text)
    await message.answer("Что вам понравилось больше всего?")
    await state.set_state(FeedbackStates.liked)

@feedback_router.message(FeedbackStates.liked)
async def process_liked(message: Message, state: FSMContext):
    """Обработчик ввода понравившихся моментов"""
    if len(message.text) < 5:
        await message.answer("Пожалуйста, напишите более развернуто")
        return
    
    await state.update_data(liked=message.text)
    await message.answer("Что вам не понравилось или что можно улучшить?")
    await state.set_state(FeedbackStates.disliked)

@feedback_router.message(FeedbackStates.disliked)
async def process_disliked(message: Message, state: FSMContext):
    """Обработчик завершения опроса"""
    await state.update_data(disliked=message.text)
    user_data = await state.get_data()
    
    save_to_json(user_data)
    
    await message.answer(
        "Спасибо за ваши ответы! Ваше мнение очень важно для нас.\n"
        "Ждем вас снова в наших музеях!",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()