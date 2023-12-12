from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import re
from helpers_for_user_understanding import get_date, find_station_and_code

def create_rzd_url(user_query, file_path='/Users/aliya/stations.json'):
    """
    Обрабатывает текстовый запрос пользователя и создает URL для поиска билетов на сайте РЖД.
    """
    query_parts = user_query.split(',')
    if len(query_parts) < 5:
        raise ValueError("Недостаточно информации в запросе")
    city_from, city_to, date,_,_= query_parts[:5]
    date = get_date(date.strip())
    code_to = find_station_and_code(city_to.strip(), file_path)[1]
    code_from = find_station_and_code(city_from.strip(), file_path)[1]
    url = f"https://pass.rzd.ru/tickets/public/ru?layer_name=e3-route&st0={city_from.strip()}&code0={code_from}&st1={city_to.strip()}&code1={code_to}&dt0={date}&tfl=3&md=0&checkSeats=0"
    return url

def get_status_of_car(car):
    if not car:  
        return ["Плацкартный", "Купе", "СВ", "Сидячий"]

    car = car.lower().strip()
    categories = ["Плацкартный", "Купе", "СВ", "Сидячий"]
    if car == '-' or car == '—':
        return categories
    
    found_categories = []

    if "плацкарт" in car or "плацкартный" in car:
        found_categories.append("Плацкартный")

    if "купе" in car:
        found_categories.append("Купе")

    if "св" in car:
        found_categories.append("СВ")
        
    if "сидячий" in car:
        found_categories.append("Сидячий")   

    return found_categories if found_categories else categories

from selenium.webdriver.common.by import By
from selenium.webdriver.common.by import By
import re

import re
from selenium.webdriver.common.by import By

async def get_trains(url, driver, first_message_from_user):
    """
    Парсит данные о поездах и доступных местах с веб-страницы РЖД по созданному URL.
    """
    driver.implicitly_wait(10)
    driver.get(url)

    user_preferences = first_message_from_user.split(',')
    preferred_car_types = get_status_of_car(user_preferences[3])  # Получение предпочтительных типов вагонов

    max_price = float('inf')
    if len(user_preferences) > 4:
        max_price_input = user_preferences[4].strip()
        if max_price_input not in ["-", "—"]:
            max_price = int(max_price_input)  

    ticket_data = {}
    route_items = driver.find_elements(By.CLASS_NAME, 'route-item')
    for item in route_items:
        class_attribute = item.get_attribute("class")
        route_times = item.find_elements(By.CLASS_NAME, 'train-info__route_time')
        times = ' - '.join([time.text for time in route_times if time.text.strip()])

        if "route-item__train-without-places" in class_attribute:
            ticket_data[times] = "Нет мест"
        else:
            match_found = False  
            car_type_items = item.find_elements(By.CLASS_NAME, 'route-carType-item')
            for car_type in car_type_items:
                car_type_text = car_type.find_element(By.CLASS_NAME, 'serv-cat').text
                price_text = car_type.find_element(By.CLASS_NAME, 'route-cartype-price-rub').text
                if car_type_text.strip() and price_text.strip():
                    price = int(re.sub("\D", "", price_text))
                    if car_type_text in preferred_car_types and price <= max_price:
                        match_found = True  
                        break

            if not match_found: 
                ticket_data[times] = f"Нет подходящих билетов дешевле {max_price}"

    return ticket_data


def create_driver(executable_path=None, headless=True):
    """
    Создает нужный нам вебдрайвер
    """

    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    if executable_path is None:
        service = Service(ChromeDriverManager().install())
    else:
        service = Service(executable_path=executable_path)

    return webdriver.Chrome(service=service, options=options)


async def handle_request(first_message_from_user):
    driver = create_driver()
    try:
        url = create_rzd_url(first_message_from_user, file_path='/Users/aliya/stations.json')
        answer_dict = await get_trains(url, driver,first_message_from_user)
        return answer_dict
    finally:
        driver.quit() 


async def get_good_trains(url, driver, first_message_from_user, train_times):
    """
    Находит подходящие билеты на поезд, чтобы отправить уведомление пользователю.
    """
    driver.implicitly_wait(10)
    driver.get(url)
    user_preferences = first_message_from_user.split(',')
    preferred_car_types = get_status_of_car(user_preferences[3])
    max_price = int(user_preferences[4].strip()) if len(user_preferences) > 4 and user_preferences[4].strip().isdigit() else float('inf')

    ticket_data = {}
    notification_messages = []  

    route_items = driver.find_elements(By.CLASS_NAME, 'route-item')
    for item in route_items:
        route_times = item.find_elements(By.CLASS_NAME, 'train-info__route_time')
        times = ' - '.join([time.text for time in route_times if time.text.strip()])

        if times not in train_times:
            continue

        available_options = []
        car_type_items = item.find_elements(By.CLASS_NAME, 'route-carType-item')
        for car_type in car_type_items:
            car_type_text = car_type.find_element(By.CLASS_NAME, 'serv-cat').text
            price_text = car_type.find_element(By.CLASS_NAME, 'route-cartype-price-rub').text
            if car_type_text and price_text:
                price = int(re.sub("\D", "", price_text))
                if car_type_text in preferred_car_types and price <= max_price:
                    available_options.append(f"{car_type_text} за {price_text}р")
        
        if available_options:
            ticket_data[times] = available_options
            message = f"На поезд {times} появились билеты: {', '.join(available_options)}!)"
            notification_messages.append(message)

    return ticket_data, notification_messages



async def handle_check_request(first_message_from_user, train_times):
    driver = create_driver()
    try:
        url = create_rzd_url(first_message_from_user, file_path='/Users/aliya/stations.json')
        answer_dict, message = await get_good_trains(url, driver,first_message_from_user,train_times)
        print(answer_dict, message)
        return answer_dict, message
        
    finally:
        driver.quit() 

first_message_from_user='Москва, Казань, 13.12, плацкарт и купе, 3200'
train_times=['23:12 - 11:01','19:16 - 07:50']

import asyncio
asyncio.run(handle_check_request(first_message_from_user, train_times))
