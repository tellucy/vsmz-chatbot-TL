from aiogram.fsm.state import StatesGroup, State

class FeedbackStates(StatesGroup):
    gender = State()
    age = State() 
    home_city = State()
    visited_city = State()
    visited_events = State()
    liked = State()        
    disliked = State()  