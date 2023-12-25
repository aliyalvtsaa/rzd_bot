from aiogram.types import KeyboardButton, ReplyKeyboardMarkup,InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from mongodb_connector import MongoDBConnector
from config import uri

db_name = "user_data"
mongo_connector = MongoDBConnector(uri, db_name)

async def get_trains(trains):
    trains_kb = InlineKeyboardBuilder()
    for key, value in trains.items():
        button_text = f"{key}⏰ {value}"
        trains_kb.add(InlineKeyboardButton(text=button_text, callback_data=key))
        print(key)
    final_button = InlineKeyboardButton(text="Все поезда выбраны", callback_data="final_choice")
    trains_kb.add(final_button)
    return trains_kb.adjust(1).as_markup(resize_keyboard = True)

yes_button = KeyboardButton(text='Да')
no_button = KeyboardButton(text='Нет')
confirmation_keyboard = ReplyKeyboardMarkup(keyboard=[[yes_button, no_button]], resize_keyboard=True, one_time_keyboard=True)

new_button = KeyboardButton(text='Новое отслеживание')
cancel_button = KeyboardButton(text='Отменить отслеживание')
process_keyboard = ReplyKeyboardMarkup(keyboard=[[new_button, cancel_button]], resize_keyboard=True)

async def get_tracks(chat_id):
    user_records = mongo_connector.get_cancel_data('chat_id', chat_id)
    cancel_items_kb = InlineKeyboardBuilder()
    for record in user_records:
        message_for_cancelling=record.get('message_for_cancelling')
        cancel_items_kb.add(InlineKeyboardButton(text=message_for_cancelling, callback_data=str(record.get('_id'))))
    return cancel_items_kb.adjust(1).as_markup(resize_keyboard = True)

