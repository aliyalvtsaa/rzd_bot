from rzd_parse_first_time import handle_check_request
from mongodb_connector import MongoDBConnector
from config import TOKEN
from config import uri
from aiogram import Bot
import asyncio
import logging

bot = Bot(token=TOKEN)
db_name = "user_data"
mongo_connector = MongoDBConnector(uri, db_name)

def should_notify_user(previous_data, current_data):
    new_trains={}
    for time, current_options in current_data.items():
        previous_options = set(previous_data.get(time, []))
        current_options_set = set(current_options)
        avaliable_trains = current_options_set - previous_options
        if avaliable_trains:
            new_trains[time] = avaliable_trains
    return new_trains

async def send_notification(chat_id, message):
    """
    Отправляет уведомление о новых билетах
    """
    try:
        await bot.send_message(chat_id, message)
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")

async def periodic_check():
    while True:
        user_records = mongo_connector.get_all_data()
        for record in user_records:
            chat_id = record["chat_id"]
            logging.info(f'Получили данные о пользователе {chat_id}')
            url = record["url"]
            max_price = record["max_price"]
            #max_price = 10000
            train_classes = record["train_classes"]
            train_times = record["train_times"]
            url = record["url"]
            id = record["_id"]
            answer_dict = await handle_check_request(url, train_classes, max_price, train_times)
            logging.info(f'Получили новые данные {answer_dict}')
            new_trains=should_notify_user(record.get("answer_dict"), answer_dict)
            if new_trains:
                logging.info(f'Получили новые места {new_trains}')
                for time, options in new_trains.items():
                    options_str = '\n'.join(f"{option} 🥳" for option in options)
                    message = f'Здравствуйте!) На поезд {time} появились билеты:\n{options_str} :\n{url}'
                    await send_notification(chat_id, message)   
            else:
                logging.info('Новые места не нашлись')       
            mongo_connector.update_user_record(id, {"answer_dict": answer_dict})

        await asyncio.sleep(30)

    
