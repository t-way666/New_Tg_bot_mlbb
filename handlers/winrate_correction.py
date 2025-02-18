def send_winrate_correction(bot):
    @bot.message_handler(commands=['winrate_correction'])
    def send_winrate_correction_message(message):
        winrate_text = "Введите ваш текущий винрейт (в процентах):"
        msg = bot.reply_to(message, winrate_text)
        bot.register_next_step_handler(msg, process_current_winrate_step, bot)

def process_current_winrate_step(message, bot):
    try:
        current_winrate = float(message.text)
        msg = bot.reply_to(message, "Введите количество уже сыгранных матчей:")
        bot.register_next_step_handler(msg, process_played_matches_step, bot, current_winrate)
    except ValueError:
        bot.reply_to(message, "Пожалуйста, введите число.")

def process_played_matches_step(message, bot, current_winrate):
    try:
        played_matches = int(message.text)
        msg = bot.reply_to(message, "Введите ожидаемый винрейт в будущих играх (в процентах):")
        bot.register_next_step_handler(msg, process_expected_winrate_step, bot, current_winrate, played_matches)
    except ValueError:
        bot.reply_to(message, "Пожалуйста, введите целое число.")

def process_expected_winrate_step(message, bot, current_winrate, played_matches):
    try:
        expected_winrate = float(message.text)
        msg = bot.reply_to(message, "Введите желаемый общий винрейт (в процентах):")
        bot.register_next_step_handler(msg, process_desired_winrate_step, bot, current_winrate, played_matches, expected_winrate)
    except ValueError:
        bot.reply_to(message, "Пожалуйста, введите число.")

def process_desired_winrate_step(message, bot, current_winrate, played_matches, expected_winrate):
    try:
        desired_winrate = float(message.text)
        additional_matches = calculate_additional_matches(current_winrate, played_matches, expected_winrate, desired_winrate)
        bot.reply_to(message, f"Вам нужно сыграть примерно {additional_matches} дополнительных матчей, чтобы достичь желаемого винрейта.")
    except ValueError:
        bot.reply_to(message, "Пожалуйста, введите число.")

def calculate_additional_matches(current_winrate, played_matches, expected_winrate, desired_winrate):
    current_wins = current_winrate / 100 * played_matches
    additional_matches = 0
    while True:
        desired_wins = desired_winrate / 100 * (played_matches + additional_matches)
        if desired_wins <= current_wins + additional_matches * (expected_winrate / 100):
            break
        additional_matches += 1
    return additional_matches