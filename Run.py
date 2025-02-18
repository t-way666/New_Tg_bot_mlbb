import logging
import telebot
from config import API_TOKEN
from handlers import start, help, winrate_correction, season_progress, rank, my_stars

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

@bot.message_handler(func=lambda message: True)
def echo(message):
    bot.reply_to(message, message.text)

if __name__ == '__main__':
    bot.polling(none_stop=True)
