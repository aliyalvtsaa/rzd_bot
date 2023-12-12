from aiogram import Router, F
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.methods.edit_message_text import EditMessageText

from keyboards import trains
from mongodb_connector import MongoDBConnector

uri = "mongodb+srv://aliyasta:2lzTBzOi5d0iplfw@cluster0.ndrzlgu.mongodb.net/?retryWrites=true&w=majority"
db_name = "user_data"
mongo_connector = MongoDBConnector(uri, db_name)
router=Router()
    
@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Добро пожаловать в бот для отслеживания билетов на поезд!♥\nОпишите через запятую\n⏩откуда\n⏪куда\n📆когда\n💵по какой максимальной цене вы хотите поехать!)\nНапример:\nМосква, Казань, 12.12, плацкарт и купе, 5000\nЕсли какая-то настройка не требуется, просто поставьте прочерк\nБот отправит поезда, на которые нет подходящих билетов, чтобы отслеживать их появление👀')
    
@router.message()
async def go(message: Message):
    trains_markup = await trains(message.text)
    user_needs=message.text
    chat_id=message.chat.id
    mongo_connector.insert_initial_data(chat_id, user_needs)
    await message.answer(f'Отлично! Выберите поезда для отслеживания:', reply_markup=trains_markup)
    
@router.callback_query(F.data)
async def train_selected(callback: CallbackQuery):
    train_time=callback.data
    chat_id = callback.message.chat.id
    mongo_connector.update_train_time(chat_id, train_time)
    await callback.message.answer(f'Отлично! Вы выбрали поезд на {train_time}')

@router.callback_query(F.data=='final_choice')
async def last_train_selected(callback: CallbackQuery):
    await callback.message.answer(f'Спасибо! Если на эти поезда появятся подходящие билеты, бот отправит уведомление✨')
