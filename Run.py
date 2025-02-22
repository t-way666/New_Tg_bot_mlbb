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
    hero_chars,
    chars_table,
    cybersport_info,
    hero_greed,
    hero_tiers,
    search_teammates,
    img_creator,
    support,
    video_guide_bot,
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
    'rank': rank.send_rank, 
    'my_stars': my_stars.send_my_stars,
    'menu': menu.send_menu,
    'hero_chars': hero_chars.register_hero_handlers,
    'chars_table': chars_table.register_handlers,
    'cybersport_info': cybersport_info.register_cybersport_handlers,
    'hero_greed': hero_greed.register_hero_greed_handlers,  # Исправлено имя функции
    'hero_tiers': hero_tiers.register_hero_tiers_handlers,  # Исправлено имя функции
    'search_teammates': search_teammates.register_handlers,
    'video_guide': video_guide_bot.register_handlers,
    'img_creator': img_creator.register_handlers,
    'support': support.register_handlers,
}

# Регистрация дополнительных обработчиков
search_teammates.register_handlers(bot)
img_creator.register_handlers(bot)
support.register_handlers(bot)
video_guide_bot.register_handlers(bot)
armor_and_resistance.register_handlers(bot)

@bot.message_handler(commands=list(command_mapping.keys()))
def handle_specific_commands(message):
    """Обработчик для специфических команд"""
    try:
        command = message.text.split()[0][1:].lower()
        if command in command_mapping:
            handler = command_mapping[command]
            # Прямой вызов обработчика для cybersport_info
            if command == 'cybersport_info':
                cybersport_info.register_cybersport_handlers(bot)(message)
                return
            # Для остальных команд с регистрацией обработчиков
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
