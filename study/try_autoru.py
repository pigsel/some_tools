
import requests
import json


PARAMS = {
        'section': "used",
        'category': "cars",
        'geo_radius': 200,
        'geo_id': [213],
        'page': 3,
        }

HEADERS = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Content-Length": "68",
        "content-type": "application/json",
        "Cookie": "suid=2b5b0c3c81f3f535518b11431ef356b2.5b87f2676f4049b5dcc1e3db46a594d3; credit_filter_promo_popup_closed=true; yandex_login=; i=a9jWEo9aWb2fnsNDhHxgxwGl7rVnaIB9dFUQEF42Yp1l84hrV+1grB8ziGzejDN8rI8xki2P2hkvOmKLOF/9yGpERbE=; mda2_beacon=1654072644985; _ym_uid=1649070110932074143; _ym_d=1654072669; credit_modal_autoshow_closed=true; _yasc=xZmbJkqRuWPrtdp8aMGqNiLeHQCBxOzBnZqxhk3FwjALIu4j; yandexuid=3981353701647430616; my=YwA%3D; counter_ga_all7=2; autoru_sid=a%3Ag62879dae2l1rj1a3mpfqpuni2rpg9rq.cd1641ead8fd046be5ee181b988bcb41%7C1653927746769.604800.V8DUQXtlJbAa9PrFZq2Qow.cmfRsvUAw8n0ZfRA661pfbW7Rl_OLxjT9zvin_dYb2A; autoruuid=g62879dae2l1rj1a3mpfqpuni2rpg9rq.cd1641ead8fd046be5ee181b988bcb41; cycada=r/031O3u5YcBlIHKSTc0r2r6qJ6aBFLP8/pXPLqxA3E=; autoru-visits-count=1; yuidlt=1; _csrf_token=4dd67a5fe580f154cdc447db1f58237f6cb1abd118acb77c; gdpr=0; ys=udn.cDpwaWdzZWw%3D%23wprid.1652094929391229-29659443128650674-sas6-5252-3ed-sas-l7-balancer-8080-BAL-264#c_chck.861672505; from=direct; from_lifetime=1654072669064; Session_id=noauth:1654072644; sso_status=sso.passport.yandex.ru:synchronized; _ym_isad=2",
        "Host": "auto.ru",
        "Origin": "https://auto.ru",
        "Referer": "https://auto.ru/moskva/cars/used/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "same-origin",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0",
        "x-client-app-version": "45.0.9526496",
        "x-client-date": "1654072706316",
        "x-csrf-token": "4dd67a5fe580f154cdc447db1f58237f6cb1abd118acb77c",
        "x-requested-with": "XMLHttpRequest",
        "x-page-request-id": "d055d5be3cc80f03a6f25e7525ce1163",
        "x-retpath-y": "https://auto.ru/moskva/cars/used/",
}

URL = 'https://auto.ru/-/ajax/desktop/listing/'
#URL = 'https://auto.ru/-/ajax/desktop/listingSpecial/'  # URL на который будет отправлен запрос

response = requests.post(URL, json=PARAMS, headers=HEADERS)

data = response.json()

with open('autoru.json', 'w') as f:
        f.write(json.dumps(data, indent=4))
