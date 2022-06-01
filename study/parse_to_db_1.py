import requests
from bs4 import BeautifulSoup


domain = 'https://gb.ru/'
start_url = 'https://gb.ru/posts'

response = requests.get(start_url)
soap = BeautifulSoup(response.text, 'lxml')

print(1)