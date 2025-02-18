def send_my_stars(bot):
    @bot.message_handler(commands=['my_stars'])
    def send_my_stars_message(message):
        my_stars_text = "Это команда для получения общего количества звезд."
        bot.reply_to(message, my_stars_text)