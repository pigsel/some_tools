"""
урок 1 - парсинг сайта пятерочки

- найти ссылку на апи,
- написать скрипт чтобы растопырить апи на словарь

"""


import requests
import json
import time

URL = 'https://5ka.ru/api/v2/special_offers/'    # ссылку выловил в броузере - исследовать - в заголовках XHR
CAT_URL = 'https://5ka.ru/api/v5/categories/'    # ссылка на категории - у меня не работает без выбора магазина
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0',
           'store': 5113}


def x5ka(url):
    result = []
    while url:
        # пока есть данные в url делаем запросы
        response = requests.get(url, headers=headers)
        data = response.json()
        result.extend(data.get('results'))    # добавляем данные из json
        url = data.get('next')   # ищем ссылку на след страницу
        time.sleep(1)    # делаем паузы между запросами чтобы сервер не завис
    return result


if __name__ == '__main__':
    categories = requests.get(CAT_URL, headers=headers)
    data = x5ka(URL)
