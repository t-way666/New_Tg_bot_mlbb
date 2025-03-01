import os
from dotenv import load_dotenv
from pathlib import Path

# Получаем путь к текущему файлу
current_file = Path(__file__)
# Путь к директории config
CONFIG_DIR = current_file.parent
# Путь к корневой директории проекта
ROOT_DIR = CONFIG_DIR.parent
# Путь к директории media
MEDIA_DIR = os.path.join(ROOT_DIR, 'media')
# Путь к файлу .env
ENV_PATH = CONFIG_DIR / '.env'

# Проверяем существование файла .env
if not ENV_PATH.exists():
    raise FileNotFoundError(f"Файл .env не найден по пути: {ENV_PATH}")

# Загружаем переменные окружения
load_dotenv(ENV_PATH)

# Получаем API токен
API_TOKEN = os.getenv('API_TOKEN')

if not API_TOKEN:
    raise ValueError(f"API_TOKEN не найден в файле {ENV_PATH}")