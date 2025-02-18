import logging
import telebot
from config import API_TOKEN
from handlers import start, help, winrate_correction, season_progress, rank, my_stars
from handlers.command_handler import handle_commands
from handlers.armor_and_resistance import armor_calculator

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot
bot = telebot.TeleBot(API_TOKEN)

# Register handlers
start.send_start(bot)
help.send_help(bot)
winrate_correction.send_winrate_correction(bot)
season_progress.send_season_progress(bot)
rank.send_rank(bot)
my_stars.send_my_stars(bot)

@bot.message_handler(commands=['start', 'help', 'winrate_correction', 'season_progress', 'rank', 'my_stars'])
def handle_commands_wrapper(message):
    handle_commands(bot, message)

@bot.message_handler(commands=['armor'])
def armor_command(message):
    armor_calculator(message, bot)

@bot.message_handler(func=lambda message: message.text.startswith('/'))
def prioritize_commands(message):
    handle_commands(bot, message)

@bot.message_handler(func=lambda message: True)
def echo(message):
    # Обработка других сообщений
    pass

if __name__ == '__main__':
    bot.polling(none_stop=True)
