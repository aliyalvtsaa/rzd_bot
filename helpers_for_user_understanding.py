import json
import Levenshtein
from datetime import datetime, timedelta



def get_date(day):
    """
    Пользователь отправляет 12.12, а мы на сайт РЖД отправим 12.12.2023!
    А если отправит 02.01, поймем что это 02.01.2024!
    """
    current_date = datetime.now()
    current_year = current_date.year
    target_date = datetime.strptime(f"{day}.{current_year}", "%d.%m.%Y")
    if target_date < current_date:
        target_date = datetime.strptime(f"{day}.{current_year + 1}", "%d.%m.%Y")

    return target_date.strftime("%d.%m.%Y")


def find_station_and_code(city_name, file_path='/Users/aliya/stations.json'):
    """
    Находит самую похожую станцию на город, который прислал пользователь.
    Например Архангельск - 'Архангельск ГОРОД', код 2010400. Хотите в Архангельск?))
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
