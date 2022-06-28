"""
урок 1 - парсинг сайта пятерочки

- найти ссылку на апи,
- написать скрипт чтобы скачать json

"""


import requests
import json
import time

URL = 'https://5ka.ru/api/v2/special_offers/'    # ссылку выловил в броузере - исследовать - в заголовках XHR
CAT_URL = 'https://5ka.ru/api/v5/categories/'    # ссылка на категории - у меня не работает без выбора магазина
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0',
           'store': 5113}


def get_products(url, params):
    result = []
    while url:
        # пока есть данные в url делаем запросы
        response = requests.get(url, headers=headers, params=params) if params else requests.get(url, headers=headers)
        params = None
        data = response.json()
        result.extend(data.get('results'))    # добавляем данные из json
        url = data.get('next')   # ищем ссылку на след страницу
        time.sleep(1)    # делаем паузы между запросами чтобы сервер не завис
    return result


def clear_name(name: str) -> str:
    tmp = name.replace('*', '').replace(',', '').replace('"', '').lower().split()
    return '_'.join(tmp)


if __name__ == '__main__':
    categories = requests.get(CAT_URL, headers=headers).json()

    for category in categories:
        category['products'] = get_products(URL, {'records_per_page': 100,
                                                  'categories': category['parent_group_code']
                                                  }
                                            )

        with open(f'jdata/{clear_name(category["parent_group_name"])}.json', 'w') as file:
            file.write(json.dumps(category))


# не работает тк сайт изменился с тех пор

