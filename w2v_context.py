PATH = '/home/vagrant/PycharmProjects/CL_Sem_1/fulltext/*.txt'

from pyspark.sql import SparkSession
from pyspark.ml.feature import Tokenizer
from pyspark.ml.feature import StopWordsRemover
from pyspark.ml.feature import Word2Vec
from pymongo import MongoClient
import re
import string


def remove_punctuation(text):
    """
    Удаление пунктуации из текста
    """
    return text.translate(str.maketrans('', '', string.punctuation))


def get_only_words(tokens):
    """
    Получение списка токенов, содержащих только слова
    """
    return list(filter(lambda x: re.match('[а-яА-Я]+', x), tokens))


spark = SparkSession \
        .builder \
        .appName("SimpleApplication") \
        .config("spark.executor.memory", "2g") \
        .config("spark.driver.memory", "2g") \
        .config("spark.memory.offHeap.enabled", True) \
        .config("spark.memory.offHeap.size", "2g") \
        .getOrCreate()

client = MongoClient('localhost', 27017) # Создаем клиент MongoDB
db = client['compling'] # Подключаемся к базе данных compling
collection = db['articles'] # Сохраняем коллекцию "articles" в переменную

text_in = ""

# Извлечение из коллекции всех текстов
for element in collection.find({"text": {"$ne" : ""}}):
    text_in += element["text"] + ".\n"

# Запись в файл текста для парсера
my_file = open("/home/vagrant/PycharmProjects/CL_Sem_1/fulltext/fulltext.txt", "w+")
my_file.write(text_in)
my_file.close()

input_file = spark.sparkContext.wholeTextFiles(PATH)

prepared_data = input_file.map(lambda x: (x[0], remove_punctuation(x[1])))
df = prepared_data.toDF()
prepared_df = df.selectExpr('_2 as text')

# Бьем на токены
tokenizer = Tokenizer(inputCol='text', outputCol='words')
words = tokenizer.transform(prepared_df)

# Убираем стоп-слова
stop_words = StopWordsRemover.loadDefaultStopWords('russian')
remover = StopWordsRemover(inputCol="words", outputCol="filtered", stopWords=stop_words)

# Строим модель
word2Vec = Word2Vec(vectorSize=50, inputCol='words', outputCol='result', minCount=2)
model = word2Vec.fit(words)

model.getVectors().show()
print(model.findSynonymsArray("школ", 5))

spark.stop()
