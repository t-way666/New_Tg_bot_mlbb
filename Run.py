import logging
import telebot
import time
from requests.exceptions import ConnectionError, ReadTimeout
from config.settings import API_TOKEN  # Изменен импорт на прямой путь
from handlers import (
    start,
    help,
    winrate_correction,
    season_progress,
    rank,
    my_stars,
    armor_and_resistance
)
from handlers.command_handler import handle_commands

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация бота
bot = telebot.TeleBot(API_TOKEN)

# Регистрация всех обработчиков
HANDLERS = [
    start.send_start,
    help.send_help,
    winrate_correction.send_winrate_correction,
    season_progress.send_season_progress,
    rank.send_rank,
    my_stars.send_my_stars,
    armor_and_resistance.register_handlers
]

# Регистрируем все обработчики
for handler in HANDLERS:
    handler(bot)

@bot.message_handler(commands=['start', 'help', 'winrate_correction', 'season_progress', 'rank', 'my_stars', 'armor_and_resistance'])
def handle_commands_wrapper(message):
    handle_commands(bot, message)

@bot.message_handler(func=lambda message: message.text.startswith('/'))
def prioritize_commands(message):
    handle_commands(bot, message)

@bot.message_handler(func=lambda message: True)
def echo(message):
    pass

def run_bot():
    """Запуск бота с обработкой ошибок и повторными попытками"""
    while True:
        try:
            logger.info("Бот запущен")
            bot.polling(none_stop=True, timeout=60)
        except ConnectionError as e:
            logger.error(f"Ошибка подключения: {e}")
            time.sleep(15)
        except ReadTimeout as e:
            logger.error(f"Таймаут чтения: {e}")
            time.sleep(15)
        except Exception as e:
            logger.error(f"Необработанная ошибка: {e}")
            time.sleep(15)
        logger.info("Переподключение...")

if __name__ == '__main__':
    run_bot()
