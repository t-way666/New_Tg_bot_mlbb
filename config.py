import os
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

# Получаем API токен из переменных окружения
API_TOKEN = os.getenv('API_TOKEN')

if not API_TOKEN:
    raise ValueError("API_TOKEN не найден в переменных окружения. Создайте файл .env и добавьте API_TOKEN=ваш_токен")