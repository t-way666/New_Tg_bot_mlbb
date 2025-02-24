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
    rank_stars,
    armor_and_resistance,
    menu,
    hero_chars,
    chars_table,
    hero_greed,
    hero_tiers,
    search_teammates,
    img_creator,
)

from handlers.command_handler import handle_commands

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'  # исправлено с "уровеньname" на "levelname"
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
    'rank_stars': rank_stars.send_rank_stars,
    'menu': menu.send_menu,
    'hero_chars': hero_chars.register_hero_handlers,
    'chars_table': chars_table.register_handlers,
    'hero_greed': hero_greed.register_hero_greed_handlers,
    'hero_tiers': hero_tiers.register_hero_tiers_handlers,
    'search_teammates': search_teammates.register_handlers,
    'img_creator': img_creator.register_handlers,
}

# Регистрация дополнительных обработчиков
search_teammates.register_handlers(bot)
img_creator.register_handlers(bot)
armor_and_resistance.register_handlers(bot)

@bot.message_handler(commands=list(command_mapping.keys()))
def handle_specific_commands(message):
    """Обработчик для специфических команд"""
    try:
        command = message.text.split()[0][1:].lower()
        if command in command_mapping:
            handler = command_mapping[command]
            # Для команд с регистрацией обработчиков
            if command in ['hero_chars', 'hero_tiers', 'hero_greed']:
                result = handler(bot)
                if result:
                    result(message)
                return
            # Для простых команд
            handler(bot)(message)
    except Exception as e:
        logger.error(f"Ошибка при обработке команды {command}: {e}")
        bot.reply_to(message, "Произошла ошибка при обработке команды. Попробуйте позже.")

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
