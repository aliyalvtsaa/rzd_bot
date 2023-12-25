from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.methods.edit_message_text import EditMessageText
from aiogram.fsm.context import FSMContext
import asyncio
from bson import ObjectId

from keyboards import get_trains
from keyboards import get_tracks
from keyboards import confirmation_keyboard
from keyboards import process_keyboard
from rzd_parse_first_time import understand_user
from rzd_parse_first_time import create_rzd_url
from rzd_parse_first_time import handle_request
from helpers_for_user_understanding import create_message
from mongodb_connector import MongoDBConnector

from config import uri


db_name = "user_data"
mongo_connector = MongoDBConnector(uri, db_name)
router=Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Добро пожаловать в бот для отслеживания билетов на поезд!♥\nОпишите в свободной форме\n⏩откуда\n⏪куда\n📆когда\n🚂каким классом\n💵по какой максимальной цене вы хотите поехать!)\nНапример:\nИщу билеты из Москвы в Казань на завтра до 5 тысяч\nБот отправит поезда, на которые нет подходящих билетов👀')

@router.message(F.text == 'Нет')
async def tell_user(message: Message):
    await message.answer('Хорошо, напишите, пожалуйста, Ваш запрос еще раз:)')
    
@router.message(F.text == 'Да')
async def go(message: Message, state: FSMContext):
    our_message = await message.answer("Ищем поезда... 🚂🚂🚂")
    await asyncio.sleep(3)
    await our_message.edit_text("Скоро найдем! ⌛")
    user_wish = await state.get_data()
    url, train_classes, max_price = create_rzd_url(user_wish['response'])
    trains = await handle_request(url, train_classes, max_price)
    if trains:
        trains_markup = await get_trains(trains)
        chat_id=message.chat.id
        await state.update_data(chat_id=chat_id, url=url, train_classes=train_classes, max_price=max_price)
        await our_message.edit_text(f'Получилось! Выберите поезда для отслеживания:', reply_markup=trains_markup)
    else:
        await our_message.edit_text(f'Кажется, на все поезда уже есть подходящие билеты🚂')
        
@router.message(F.text == 'Новое отслеживание')
async def new_track(message: Message):
    await message.answer('Отлично! Введите новый запрос👀')

@router.message(F.text == 'Отменить отслеживание')
async def cancel_track(message: Message):
    chat_id=message.chat.id
    cancel_markup = await get_tracks(chat_id)
    await message.answer(f'Выберите отслеживания для отмены:', reply_markup=cancel_markup)
      
@router.message()
async def ask_user(message: Message, state: FSMContext):
    response, No_date=understand_user(message.text)
    if not all(key in response for key in ['city_from', 'city_to']) or No_date:
        await message.answer('Кажется, чего-то не хватает:\nПожалуйста, укажите в запросе города отправления и прибытия, а также день, когда хотите отправиться')
    else:
        message_for_user, message_for_cancelling = create_message(response)
        await message.answer(message_for_user, reply_markup=confirmation_keyboard)
        await state.update_data(response=response, message_for_cancelling=message_for_cancelling)
        
@router.callback_query(F.data)
async def train_selected(callback: CallbackQuery, state: FSMContext):
    if callback.data=='final_choice':
        await callback.message.answer(f'Спасибо! Если на эти поезда появятся подходящие билеты, бот отправит уведомление✨', reply_markup=process_keyboard)
    elif callback.data.isalnum():
        object_id = ObjectId(callback.data)
        mongo_connector = MongoDBConnector(uri, db_name)
        record = mongo_connector.get_record_by_id(object_id)
        message_for_cancelling = record.get('message_for_cancelling')
        mongo_connector.delete_record_by_id(object_id)
        await callback.message.answer(f'Отлично!) Отслеживание "{message_for_cancelling}" удалено')
    else:
        mongo_connector = MongoDBConnector(uri, db_name)
        train_time=callback.data
        user_data = await state.get_data()
        mongo_connector.insert_or_update_user_data(user_data, train_time)
        await callback.message.answer(f'Отлично! Вы выбрали поезд на {train_time}')

