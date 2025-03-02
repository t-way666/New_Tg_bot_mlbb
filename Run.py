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
    damage_calculator,
    hero_stats,
)

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)

# Инициализация бота с явным указанием хранилища состояний
state_storage = StateMemoryStorage()
bot = telebot.TeleBot(API_TOKEN, state_storage=state_storage)

# Регистрация обработчиков команд
@bot.message_handler(commands=['start'])
def start_command(message):
    start.send_start(bot)(message)

@bot.message_handler(commands=['help'])
def help_command(message):
    help.send_help(bot)(message)

@bot.message_handler(commands=['menu'])
def menu_command(message):
    menu.send_menu(bot)(message)

@bot.message_handler(commands=['winrate_correction'])
def winrate_correction_command(message):
    winrate_correction.send_winrate_correction(bot)(message)

@bot.message_handler(commands=['season_progress'])
def season_progress_command(message):
    season_progress.send_season_progress(bot)(message)

@bot.message_handler(commands=['rank_stars'])
def rank_stars_command(message):
    rank_stars.send_rank_stars(bot)(message)

@bot.message_handler(commands=['armor_and_resistance'])
def armor_and_resistance_command(message):
    try:
        logger.info(f"Вызов команды /armor_and_resistance для пользователя {message.from_user.id}")
        # Отправляем простое сообщение для подтверждения получения команды
        bot.send_message(message.chat.id, "Запускаю калькулятор защиты и снижения урона...")
        # Вызываем функцию armor_calculator
        armor_and_resistance.armor_calculator(message, bot)
    except Exception as e:
        logger.error(f"Ошибка при обработке команды /armor_and_resistance: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка в калькуляторе защиты. Пожалуйста, попробуйте позже.")

@bot.message_handler(commands=['damage_calculator'])
def damage_calculator_command(message):
    try:
        logger.info(f"Вызов команды /damage_calculator для пользователя {message.from_user.id}")
        # Отправляем простое сообщение для подтверждения получения команды
        bot.send_message(message.chat.id, "Запускаю калькулятор урона...")
        # Вызываем функцию damage_calc
        damage_calculator.damage_calc(message, bot)
    except Exception as e:
        logger.error(f"Ошибка при обработке команды /damage_calculator: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка в калькуляторе урона. Пожалуйста, попробуйте позже.")

@bot.message_handler(commands=['hero_chars'])
def hero_chars_command(message):
    hero_chars.register_hero_handlers(bot)(message)

@bot.message_handler(commands=['chars_table'])
def chars_table_command(message):
    chars_table.register_handlers(bot)(message)

@bot.message_handler(commands=['hero_greed'])
def hero_greed_command(message):
    hero_greed.register_hero_greed_handlers(bot)(message)

@bot.message_handler(commands=['hero_tiers'])
def hero_tiers_command(message):
    hero_tiers.register_hero_tiers_handlers(bot)(message)

@bot.message_handler(commands=['search_teammates'])
def search_teammates_command(message):
    search_teammates.register_search_teammates_handlers(bot)(message)

@bot.message_handler(commands=['hero_stats'])
def hero_stats_command(message):
    hero_stats.register_hero_stats_handlers(bot)(message)

# Регистрация обработчиков для команд /heroes_list и /compare_heroes
# происходит внутри функции register_hero_stats_handlers

# Обработчик для всех остальных сообщений
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    handle_commands(message, bot)

# Функция для запуска бота с обработкой ошибок
def run_bot():
    while True:
        try:
            logger.info("Запуск бота...")
            bot.polling(none_stop=True, interval=1)
        except ConnectionError as e:
            logger.error(f"Ошибка соединения: {e}")
            time.sleep(15)
        except ReadTimeout as e:
            logger.error(f"Таймаут чтения: {e}")
            time.sleep(15)
        except Exception as e:
            logger.error(f"Необработанная ошибка: {e}")
            time.sleep(15)

if __name__ == "__main__":
    run_bot()
