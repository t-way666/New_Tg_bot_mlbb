def send_winrate_correction(bot):
    @bot.message_handler(commands=['winrate_correction'])
    def send_winrate_correction_message(message):
        winrate_text = "Это команда для расчета коррекции винрейта."
        bot.reply_to(message, winrate_text)