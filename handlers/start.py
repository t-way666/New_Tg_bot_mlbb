def send_start(bot):
    @bot.message_handler(commands=['start'])
    def send_start_message(message):
        user_first_name = message.from_user.first_name
        start_text = (
            f"Привет, {user_first_name}\n"
            "Добро пожаловать в нашего телеграм бота.\n"
            "Вот команды, которые я понимаю:\n\n"
            
            "/start — Начать или перезапустить бота\n\n"
            "/winrate_correction — Узнать, сколько матчей нужно сыграть для повышения винрейта\n\n"
            "/season_progress — Посчитать, сколько ещё игр нужно до желаемого ранга (учитывая начало сезона)\n\n"
            "/rank — Определить ваш ранг по количеству звёзд\n\n"
            "/my_stars — Узнать общее количество звёзд по рангу\n\n"
            "/help — Помощь\n\n"
        )
        bot.reply_to(message, start_text)
    return send_start_message