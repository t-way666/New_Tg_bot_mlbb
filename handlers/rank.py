def send_rank(bot):
    @bot.message_handler(commands=['rank'])
    def send_rank_message(message):
        rank_text = "Это команда для определения ранга."
        bot.reply_to(message, rank_text)
    return send_rank_message