import requests
import pymongo
from pymongo import MongoClient
from bs4 import BeautifulSoup


client = MongoClient('localhost', 27017) # Создаем клиент MongoDB
db = client['compling'] # Подключаемся к базе данных compling
collection = db['articles'] # Сохраняем коллекцию "articles" в переменную


# Задаем URL-адрес сайта для парсинга
url = 'https://bloknot-volgograd.ru'

# Создаем запрос, в ходе которого получаем html-документ по указанной ссылке
response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')

# Ищем в выдаче список <ul>, принадлежащий классу bigline, так как именно там
# содержатся последние новости сайта
news = soup.find_all('ul', class_='bigline')

# В полученном контейнере перебираем каждый элемент списка <li>, так как это
# и есть нужные нам новости
for new in news:
    lis = new.find_all('li')

# Цепляем необходимые данные каждой новости
for li in lis:
    # Название статьи, содержится в теге <a> класса "sys"
    article_name = li.find('a', class_='sys').text

    insterted_name = {
        "name": article_name
    }

    collection.insert_many([insterted_name])
    print(article_name)

# Записываем данные в БД
