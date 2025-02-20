import logging
import telebot
import time
from requests.exceptions import ConnectionError, ReadTimeout
from config.settings import API_TOKEN
from handlers import (
    start,
    help,
    winrate_correction,
    season_progress,
    rank,
    my_stars,
    armor_and_resistance,
    menu,
    hero_chars
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

# Словарь соответствия команд и обработчиков
command_mapping = {
    'start': start.send_start,
    'help': help.send_help,
    'winrate_correction': winrate_correction.send_winrate_correction,
    'season_progress': season_progress.send_season_progress,
    'rank': rank.send_rank, 
    'my_stars': my_stars.send_my_stars,
    'menu': menu.send_menu,
    'hero_chars': hero_chars.register_hero_handlers
}

# Регистрируем обработчики
hero_chars.register_hero_handlers(bot)

@bot.message_handler(commands=list(command_mapping.keys()))
def handle_specific_commands(message):
    """Обработчик для специфических команд"""
    command = message.text.split()[0][1:].lower()
    if command in command_mapping:
        handler = command_mapping[command]
        if command == 'hero_chars':
            handler(bot)
            return
        handler(bot)(message)

# Регистрируем armor_and_resistance отдельно
armor_and_resistance.register_handlers(bot)

@bot.message_handler(func=lambda message: message.text.startswith('/'))
def prioritize_commands(message):
    handle_commands(bot, message)

def run_bot():
    """Запуск бота с обработкой ошибок"""
    while True:
        try:
            logger.info("Бот запущен")
            bot.polling(none_stop=True, timeout=60)
        except (ConnectionError, ReadTimeout) as e:
            logger.error(f"Ошибка соединения: {e}")
            time.sleep(15)
        except Exception as e:
            logger.error(f"Необработанная ошибка: {e}")
            time.sleep(15)
        logger.info("Переподключение...")

if __name__ == '__main__':
    run_bot()
