from handlers.command_handler import handle_commands

def send_winrate_correction(bot):
    @bot.message_handler(commands=['winrate_correction'])
    def send_winrate_correction_message(message):
        winrate_text = "Введите ваш текущий винрейт:"
        msg = bot.reply_to(message, winrate_text)
        bot.register_next_step_handler(msg, process_current_winrate_step, bot)
    return send_winrate_correction_message

def process_current_winrate_step(message, bot):
    if message.text.startswith('/'):
        handle_commands(bot, message)
        return
    try:
        current_winrate = float(message.text)
        if current_winrate < 0 or current_winrate > 100:
            raise ValueError
        msg = bot.reply_to(message, "Введите количество уже сыгранных матчей:")
        bot.register_next_step_handler(msg, process_played_matches_step, bot, current_winrate)
    except ValueError:
        msg = bot.reply_to(message, "Пожалуйста, введите число от 0 до 100.")
        bot.register_next_step_handler(msg, process_current_winrate_step, bot)

def process_played_matches_step(message, bot, current_winrate):
    if message.text.startswith('/'):
        handle_commands(bot, message)
        return
    try:
        played_matches = int(message.text)
        msg = bot.reply_to(message, "Введите ожидаемый винрейт в будущих играх:")
        bot.register_next_step_handler(msg, process_expected_winrate_step, bot, current_winrate, played_matches)
    except ValueError:
        msg = bot.reply_to(message, "Пожалуйста, введите целое число.")
        bot.register_next_step_handler(msg, process_played_matches_step, bot, current_winrate)

def process_expected_winrate_step(message, bot, current_winrate, played_matches):
    if message.text.startswith('/'):
        handle_commands(bot, message)
        return
    try:
        expected_winrate = float(message.text)
        if expected_winrate < 0 or expected_winrate > 100:
            raise ValueError
        msg = bot.reply_to(message, "Введите желаемый общий винрейт:")
        bot.register_next_step_handler(msg, process_desired_winrate_step, bot, current_winrate, played_matches, expected_winrate)
    except ValueError:
        msg = bot.reply_to(message, "Пожалуйста, введите число от 0 до 100.")
        bot.register_next_step_handler(msg, process_expected_winrate_step, bot, current_winrate, played_matches)

def process_desired_winrate_step(message, bot, current_winrate, played_matches, expected_winrate):
    if message.text.startswith('/'):
        handle_commands(bot, message)
        return
    try:
        desired_winrate = float(message.text)
        if desired_winrate < 0 or desired_winrate > 100:
            raise ValueError
        additional_matches = calculate_additional_matches(current_winrate, played_matches, expected_winrate, desired_winrate)
        bot.reply_to(message, f"Вам нужно сыграть примерно {additional_matches} дополнительных матчей с винрейтом {expected_winrate}, чтобы достичь желаемого общего винрейта в {desired_winrate}%.")
    except ValueError:
        msg = bot.reply_to(message, "Пожалуйста, введите число от 0 до 100.")
        bot.register_next_step_handler(msg, process_desired_winrate_step, bot, current_winrate, played_matches, expected_winrate)

def calculate_additional_matches(current_winrate, played_matches, expected_winrate, desired_winrate):
    current_wins = current_winrate / 100 * played_matches
    additional_matches = 0
    while True:
        total_matches = played_matches + additional_matches
        desired_wins = desired_winrate / 100 * total_matches
        if desired_wins <= current_wins + additional_matches * (expected_winrate / 100):
            break
        additional_matches += 1
        if additional_matches > 100000:  # Условие выхода для предотвращения бесконечного цикла
            return -1  # Возвращаем -1, если не удалось найти решение
    return additional_matches