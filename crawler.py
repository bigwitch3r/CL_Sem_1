import requests
import pymongo
from pymongo import MongoClient
from bs4 import BeautifulSoup
import datetime

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

    # Ссылку на статью берем из атрибута href тега <a> класса "sys"
    article_link = li.find('a', class_='sys')
    link = article_link['href']

    pub_date = li.find('span', class_='botinfo').text
    date = pub_date.split(' ')

    if collection.count_documents({"name": article_name}):
        print("This article already exists\n")
    else:
        insert = {
            "name": article_name,
            "link": url + link
        }
        collection.insert_many([insert])
