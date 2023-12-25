import re
import requests
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from helpers_for_user_understanding import get_date, find_station_and_code

def understand_user(user_query):
    request = {'text': user_query}
    url = 'http://94.228.122.135:8000/process'
    response = requests.post(url, json=request).json()
    No_date = False
    try:
        response['day']=get_date(response['day'])
    except:
        No_date = True
    return response, No_date

def create_rzd_url(response):
    """
    Обрабатывает запрос пользователя и создает URL для поиска билетов на сайте РЖД.
    """
    city_to = response['city_to']
    city_from = response['city_from']
    date = response['day']
    code_to = find_station_and_code(city_to, 'stations.json')[1]
    code_from = find_station_and_code(city_from, 'stations.json')[1]
    station_to = find_station_and_code(city_to, 'stations.json')[0]
    station_from = find_station_and_code(city_from, 'stations.json')[0]
    
    if 'train_class' in response and response['train_class'] != '':
        train_classes = response['train_class'].split(',')
    else:
        train_classes='all'
        
    if 'price' in response and response['price'] != '':
        max_price = int(response['price'])
    else:
        max_price = 10000000
        
    url = f"https://pass.rzd.ru/tickets/public/ru?layer_name=e3-route&st0={station_from}&code0={code_from}&st1={station_to}&code1={code_to}&dt0={date}&tfl=3&md=0&checkSeats=0"
    logging.info(url)
    return url, train_classes, max_price

async def get_trains(url, driver, train_classes, max_price):
    """
    Парсит данные о поездах и доступных местах с веб-страницы РЖД по созданному URL.
    """
    max_attempts = 5
    for attempt in range(max_attempts):
        try:
            driver.implicitly_wait(10)
            driver.get(url)

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
                            if train_classes!='all':
                                if car_type_text in train_classes and price <= max_price:
                                    match_found = True  
                                    break
                            else:
                                if price <= max_price:
                                    match_found = True  
                                    break
                    if not match_found: 
                        ticket_data[times] = f"Нет подходящих билетов"

            return ticket_data
        except WebDriverException as e:
            if attempt < max_attempts - 1:
                print(f"Ошибка подключения, попытка {attempt + 1} из {max_attempts}: {e}")
                time.sleep(5)  
            else:
                raise e 

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

async def handle_request(url, train_classes, max_price):
    driver = create_driver()
    try:
        answer_dict = await get_trains(url, driver, train_classes, max_price)   
        return answer_dict
    finally:
        driver.quit() 
        
async def handle_check_request(url, train_classes, max_price, train_times):
    driver = create_driver()
    try:
        answer_dict = await get_good_trains(url, driver, train_classes, max_price, train_times)
        return answer_dict
    finally:
        driver.quit() 

async def get_good_trains(url, driver, train_classes, max_price, train_times):
    """
    Находит подходящие билеты на поезд, чтобы отправить уведомление пользователю.
    """
    max_attempts = 5
    for attempt in range(max_attempts):
        try:
            driver.implicitly_wait(10)
            driver.get(url)
            ticket_data = {}

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
                        if train_classes!='all':
                            if car_type_text in train_classes and price <= max_price:
                                available_options.append(f"{car_type_text} за {price_text}р")
                        else:
                            if price <= max_price:
                                    available_options.append(f"{car_type_text} за {price_text}р")
                        
                if available_options:
                    ticket_data[times] = available_options
            return ticket_data
        
        except WebDriverException as e:
            if attempt < max_attempts - 1:
                print(f"Ошибка подключения, попытка {attempt + 1} из {max_attempts}: {e}")
                time.sleep(5)  
            else:
                raise e 