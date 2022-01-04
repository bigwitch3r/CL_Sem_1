import requests
import pymongo
from pymongo import MongoClient
from bs4 import BeautifulSoup
from datetime import timedelta
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
    article_name = li.find('a', class_='sys').text.strip()
    print(article_name)

    # Ссылку на статью берем из атрибута href тега <a> класса "sys"
    article_link = li.find('a', class_='sys')
    link = article_link['href']

    # Тянем дату публикации
    pub_date = li.find('span', class_='botinfo').text
    date = pub_date.split(' ')
    article_date = date[1]

    # Преобразуем дату публикации из слов в конкретные даты
    # На сайте все даты кроме "сегодня" и "вчера" записаны
    # в формате ДД.ММ.ГГГГ
    if article_date == "сегодня":
        dt = datetime.date.today()
        normal_date = dt.strftime("%d.%m.%Y")

    if article_date == "вчера":
        dt = datetime.date.today() - timedelta(days=1)
        normal_date = dt.strftime("%d.%m.%Y")

    # Получаем данные о количестве комментариев
    comments_count = li.find('a', class_='comcount').text.strip()

    # Формируем полную ссылку на новость и получаем ее HTML-файл
    new_link = url + link
    article = requests.get(new_link)
    new_soup = BeautifulSoup(article.text, 'lxml')

    # Получаем текст новости
    full_text = new_soup.find_all('div', class_='news-text')

    for p in full_text:
        paragraphs = p.find_all('p')

    article_text = []

    for paragraph in paragraphs:
        article_text.append(paragraph.text.strip())

    article_text = ' '.join(article_text)

    # Получаем ссылку на видео, если она есть
    video_soup = new_soup.find_all('iframe', attrs={"src": True})

    video_link = "None"

    for video in video_soup:
        if str(video).find("youtube") > -1:
            video_link = video['src']

    # Проверка на уникальность статьи
    if collection.count_documents({"name": article_name}):
        # Получаем данные о количестве комментариев
        comments_count = li.find('a', class_='comcount').text.replace(' ', '')

        # Обновляем данные о количестве комментариев
        filter = {'name': article_name}
        new_values = {"$set": {"comments": comments_count}}
        collection.update_one(filter, new_values)
    else:
        insert = {
            "name": article_name,
            "date": normal_date,
            "link": url + link,
            "text": article_text,
            "video": video_link,
            "comments": comments_count,
            "contains": "",
            "tonalty": ""
        }
        collection.insert_many([insert])
