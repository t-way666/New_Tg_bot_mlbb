def send_help(bot):
    @bot.message_handler(commands=['help'])
    def send_help_message(message):
        help_text = "Это команда помощи. Как-нибудь потом доделаю"
        bot.reply_to(message, help_text)
    return send_help_message