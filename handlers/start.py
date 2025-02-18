def send_start(bot):
    @bot.message_handler(commands=['start'])
    def send_start_message(message):
        user_first_name = message.from_user.first_name
        start_text = (
            f"Привет, {user_first_name}\n"
            "Добро пожаловать в нашего телеграм бота.\n"
            "Вот команды, которые я понимаю:\n\n"
            
            "/start — Начать или перезапустить бота\n\n"
            "/armor_and_resistance — Калькулятор защиты и снижения урона\n\n"
            "/help — Помощь\n\n"
            "/my_stars — Узнать общее количество звёзд по рангу\n\n"
            "/rank — Определить ваш ранг по количеству звёзд\n\n"
            "/season_progress — Посчитать, сколько ещё игр нужно до желаемого ранга (учитывая начало сезона)\n\n"
            "/winrate_correction — Корректировка винрейта\n\n"
        )
        bot.reply_to(message, start_text)
    return send_start_message