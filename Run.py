import logging
import telebot
import time
from telebot.storage import StateMemoryStorage
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
)

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация бота с явным указанием хранилища состояний
state_storage = StateMemoryStorage()
bot = telebot.TeleBot(API_TOKEN, state_storage=state_storage)

# Обработчик для сброса состояний при получении любой команды
@bot.message_handler(func=lambda message: message.text and message.text.startswith('/'), is_priority=True)
def reset_state_handler(message):
    """Обработчик для сброса состояний при получении любой команды"""
    try:
        command = message.text.split()[0].lower()
        logger.info(f"Получена команда {command} от пользователя {message.from_user.id}")
        
        # Сбрасываем состояние пользователя
        try:
            current_state = bot.get_state(message.from_user.id, message.chat.id)
            if current_state:
                logger.info(f"Сброс состояния пользователя {message.from_user.id} из состояния {current_state}")
                bot.delete_state(message.from_user.id, message.chat.id)
                logger.info(f"Состояние пользователя {message.from_user.id} успешно сброшено")
        except Exception as state_error:
            logger.error(f"Ошибка при сбросе состояния: {state_error}")
    except Exception as e:
        logger.error(f"Ошибка в обработчике сброса состояний: {e}")

# Регистрация обработчиков команд
start_handler = start.send_start(bot)
help_handler = help.send_help(bot)
menu_handler = menu.send_menu(bot)
winrate_correction_handler = winrate_correction.send_winrate_correction(bot)
season_progress_handler = season_progress.send_season_progress(bot)
rank_stars_handler = rank_stars.send_rank_stars(bot)
hero_chars_handler = hero_chars.register_hero_handlers(bot)
chars_table_handler = chars_table.register_handlers(bot)
hero_greed_handler = hero_greed.register_hero_greed_handlers(bot)
hero_tiers_handler = hero_tiers.register_hero_tiers_handlers(bot)

# Регистрация обработчиков состояний и callback-запросов
search_teammates.register_handlers(bot)
armor_and_resistance.register_handlers(bot)

# Добавляем обработчик для отладки всех сообщений
@bot.message_handler(func=lambda message: True, is_priority=False)
def debug_all_messages(message):
    """Обработчик для отладки всех сообщений"""
    logger.debug(f"Получено сообщение: '{message.text}' от пользователя {message.from_user.id}")
    # Не обрабатываем сообщение, просто логируем

# Добавляем обработчик для отладки всех callback-запросов
@bot.callback_query_handler(func=lambda call: True, is_priority=False)
def debug_all_callbacks(call):
    """Обработчик для отладки всех callback-запросов"""
    logger.debug(f"Получен callback: '{call.data}' от пользователя {call.from_user.id}")
    # Не обрабатываем callback, просто логируем

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
