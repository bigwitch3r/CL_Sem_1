import pymongo
from pymongo import MongoClient
from bs4 import BeautifulSoup
from bson.objectid import ObjectId
import tonality

#Функция для извлечения текста из коллекции
def text_input(collection):
    # Тект для томита-парсера
    text_in = ""
    #Извлечение из коллекции всех текстов
    for element in collection.find({"text": {"$ne" : ""}}):
        text_in += str(element["_id"]) + ". " + element["text"] + ".\n"
    #Запись в файл текста для парсера
    my_file = open("/home/vagrant/tomita-parser/build/bin/test.txt", "w+")
    my_file.write(text_in)
    my_file.close()

def get_contains(contains):
    #Получение переработанного текста из файла
    my_file = open("/home/vagrant/tomita-parser/build/bin/facts.txt", "r")

    index = ""
    #Обработка полученного текста из файла
    while True:
        line = my_file.readline().replace("\n", "")
        #Получение _id для записи
        if (line.find("61",0,5) != -1):
            index = line.replace(" . ", "")
            contains[index] = ""
        #Выбор строки где упоминается личность или достопримечательность
        else:
            if (line.find("Contains") != -1 and pre_line.find("}") == -1):
                contains[index] += pre_line

        pre_line = line
        if not line:
            break

    my_file.close()
    return contains

if __name__ == '__main__':
    client = MongoClient('localhost', 27017)  # Создаем клиент MongoDB
    db = client['compling']  # Подключаемся к базе данных compling
    collection = db['articles']  # Сохраняем коллекцию "articles" в переменную

    text_input(collection)
    #Словарь для contains
    contains = {}
    contains = get_contains(contains)

    #Присваиваем contains упоминания о персонах и достопримечательностях
    for key, value in contains.items():
        collection.update_one({"_id": ObjectId(key)}, {"$set": {"contains": value}})

    #Определение тональности высказываний
    tonality.collection_tonalty(collection)
    # for element in collection.find():
    #     print(str(element["_id"]) + ":" + element["contains"])