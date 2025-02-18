import logging
import telebot
import time
import sys
from requests.exceptions import ConnectionError, ReadTimeout
from telebot.apihelper import ApiException
from config import API_TOKEN
from handlers import start, help, winrate_correction, season_progress, rank, my_stars, armor_and_resistance
from handlers.command_handler import handle_commands

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def run_bot():
    while True:
        try:
            logger.info("Запуск бота...")
            # Инициализация бота
            bot = telebot.TeleBot(API_TOKEN)

            # Регистрация обработчиков
            start.send_start(bot)
            help.send_help(bot)
            winrate_correction.send_winrate_correction(bot)
            season_progress.send_season_progress(bot)
            rank.send_rank(bot)
            my_stars.send_my_stars(bot)
            armor_and_resistance.register_handlers(bot)

            @bot.message_handler(commands=['start', 'help', 'winrate_correction', 
                                        'season_progress', 'rank', 'my_stars', 
                                        'armor_and_resistance'])
            def handle_commands_wrapper(message):
                try:
                    handle_commands(bot, message)
                except Exception as e:
                    logger.error(f"Ошибка при обработке команды: {e}")
                    bot.reply_to(message, "Произошла ошибка при обработке команды. Попробуйте позже.")

            @bot.message_handler(func=lambda message: message.text.startswith('/'))
            def prioritize_commands(message):
                try:
                    handle_commands(bot, message)
                except Exception as e:
                    logger.error(f"Ошибка при обработке команды: {e}")
                    bot.reply_to(message, "Произошла ошибка при обработке команды. Попробуйте позже.")

            @bot.message_handler(func=lambda message: True)
            def echo(message):
                pass

            # Запуск бота с обработкой исключений
            bot.infinity_polling(timeout=60, long_polling_timeout=60)

        except (ConnectionError, ReadTimeout) as e:
            logger.error(f"Ошибка подключения: {e}")
            time.sleep(5)  # Ждем 5 секунд перед повторной попыткой
            continue
        except ApiException as e:
            logger.error(f"Ошибка API Telegram: {e}")
            time.sleep(5)
            continue
        except Exception as e:
            logger.error(f"Неожиданная ошибка: {e}")
            time.sleep(5)
            continue

if __name__ == '__main__':
    run_bot()
