def send_season_progress(bot):
    @bot.message_handler(commands=['season_progress'])
    def send_season_progress_message(message):
        season_progress_text = "Это команда для расчета прогресса сезона."
        bot.reply_to(message, season_progress_text)
    return send_season_progress_message