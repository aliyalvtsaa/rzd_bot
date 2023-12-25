import json
import Levenshtein
from datetime import datetime, timedelta

def get_date(day):
    """
    Преобразует строку 'day' в дату формата 'ДД.ММ.ГГГГ'.
    Принимает как дни относительно сегодня ('1' для завтра), так и конкретные даты ('ДД.ММ').
    
    Пользователь отправляет 12.12, а мы на сайт РЖД отправим 12.12.2023!
    А если отправит 02.01, поймем что это 02.01.2024! 
    """
    current_date = datetime.now()
    current_year = current_date.year

    if day.isdigit():
        day_offset = int(day)
        target_date = current_date + timedelta(days=day_offset)
    else:
        target_date = datetime.strptime(f"{day}.{current_year}", "%d.%m.%Y")
        if target_date < current_date:
            target_date = datetime.strptime(f"{day}.{current_year + 1}", "%d.%m.%Y")

    return target_date.strftime("%d.%m.%Y")

def find_station_and_code(city_name, file_path='stations.json'):
    """
    Находит самую похожую станцию на город, который прислал пользователь.
    Например Архангельск - 'Архангельск ГОРОД', код 2010400. Хотите в Архангельск?))
    Возвращает станцию и ее код.
    """

    with open(file_path, 'r', encoding='utf-8') as file:
        stations_dict = json.load(file)
    closest_station = None
    closest_distance = float('inf')
    for station in stations_dict.keys():
        distance = Levenshtein.distance(city_name.lower(), station.lower())
        if distance < closest_distance:
            closest_distance = distance
            closest_station = station

    return closest_station, stations_dict[closest_station]

def create_message(response):
    message = f"Верно ли, что Вы хотите поехать\n📍из города {response['city_from']}\n📍в город {response['city_to']}\n 📅{response['day']}"
    if 'train_class' in response and response['train_class']:
        message += f"\n🚂классами {response['train_class']}"
    if 'price' in response and response['price']:
        message += f"\n💵до {response['price']} рублей"
    message += "?"
    message_for_cancelling = f"Из города {response['city_from']} в город {response['city_to']} {response['day']} "
    if 'train_class' in response and response['train_class']:
        message_for_cancelling += f"классами {response['train_class']} "
    if 'price' in response and response['price']:
        message_for_cancelling += f"💵до {response['price']} рублей"
    return message, message_for_cancelling