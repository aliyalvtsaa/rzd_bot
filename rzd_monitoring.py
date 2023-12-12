from rzd_parse_first_time import handle_check_request
from mongodb_connector import MongoDBConnector
from config import TOKEN
from aiogram import Bot

bot = Bot(token=TOKEN)
uri = "mongodb+srv://aliyasta:2lzTBzOi5d0iplfw@cluster0.ndrzlgu.mongodb.net/?retryWrites=true&w=majority"
db_name = "user_data"
mongo_connector = MongoDBConnector(uri, db_name)

def should_notify_user(previous_data, current_data):
    if not previous_data:
        return True
    
    for time, current_options in current_data.items():
        previous_options = set(previous_data.get(time, []))
        current_options_set = set(current_options)
        if current_options_set - previous_options:
            return True

    return False


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
        user_records = mongo_connector.get_all_user_data()

        for record in user_records:
            chat_id = record["chat_id"]
            user_needs = record["user_needs"]
            train_times = ['20:40 - 08:00']

            answer_dict, messages = await handle_check_request(user_needs, train_times)

            if should_notify_user(record.get("answer_dict"), answer_dict):
                for i, message in enumerate(messages):
                    time_key = list(answer_dict.keys())[i]
                    if time_key not in record.get("answer_dict", {}) or \
                       set(answer_dict[time_key]) != set(record["answer_dict"].get(time_key, [])):
                        await send_notification(chat_id, message)

                mongo_connector.update_user_record(chat_id, {"answer_dict": answer_dict})

        await asyncio.sleep(30)

    