from telebot import types
import logging

# Настраиваем логирование
logger = logging.getLogger(__name__)

# Удаляем импорт handle_commands, так как он вызывает циклическую зависимость
# Вместо этого можно добавить проверку на команды внутри функций

def send_winrate_correction(bot):
    @bot.message_handler(commands=['winrate_correction'])
    def send_winrate_correction_message(message):
        winrate_text = "Введите ваш текущий винрейт:"
        msg = bot.reply_to(message, winrate_text)
        bot.register_next_step_handler(msg, process_current_winrate_step, bot)
    return send_winrate_correction_message

def process_current_winrate_step(message, bot):
    if message.text.startswith('/'):
        # Вместо вызова handle_commands просто прерываем текущую операцию
        bot.reply_to(message, "Операция прервана. Используйте /help для списка команд.")
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
        bot.reply_to(message, "Операция прервана. Используйте /help для списка команд.")
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
        bot.reply_to(message, "Операция прервана. Используйте /help для списка команд.")
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
        bot.reply_to(message, "Операция прервана. Используйте /help для списка команд.")
        return
    try:
        desired_winrate = float(message.text)
        if desired_winrate < 0 or desired_winrate > 100:
            raise ValueError
        additional_matches = calculate_additional_matches(current_winrate, played_matches, expected_winrate, desired_winrate)
        if additional_matches == -1:
            bot.reply_to(message, "Невозможно достичь желаемого винрейта с указанным ожидаемым винрейтом в дополнительных матчах. Желанный винрейт не может быть выше ожидаемого винрейта в дополнительных матчах.")
        else:
            bot.reply_to(message, f"Вам нужно сыграть примерно {additional_matches} дополнительных матчей с винрейтом {expected_winrate}, чтобы достичь желаемого общего винрейта в {desired_winrate}%.")
    except ValueError:
        msg = bot.reply_to(message, "Пожалуйста, введите число от 0 до 100.")
        bot.register_next_step_handler(msg, process_desired_winrate_step, bot, current_winrate, played_matches, expected_winrate)

def calculate_additional_matches(current_winrate, played_matches, expected_winrate, desired_winrate):
    if desired_winrate > expected_winrate:
        return -1  # Возвращаем -1, если желаемый винрейт больше ожидаемого винрейта в дополнительных матчах

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

def winrate_calculator(message, bot):
    """Функция-обработчик команды /winrate_correction"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn = types.InlineKeyboardButton("Начать расчет", callback_data="start_wr_calc")
    markup.add(btn)
    
    bot.send_message(
        message.chat.id,
        "Калькулятор корректировки винрейта поможет узнать,\n"
        "сколько игр нужно сыграть для достижения желаемого процента побед.",
        reply_markup=markup
    )

def register_handlers(bot):
    """Регистрация всех обработчиков для работы с винрейтом"""
    user_data = {}

    @bot.callback_query_handler(func=lambda call: call.data == "start_wr_calc")
    def handle_start_calculation(call):
        msg = bot.send_message(
            call.message.chat.id,
            "Введите текущий винрейт (0-100%):"
        )
        bot.register_next_step_handler(msg, process_current_winrate, bot)
        bot.answer_callback_query(call.id)
        bot.delete_message(call.message.chat.id, call.message.message_id)

    def process_current_winrate(message, bot):
        try:
            current_wr = float(message.text)
            if not 0 <= current_wr <= 100:
                raise ValueError
            
            chat_id = message.chat.id
            user_data[chat_id] = {'current_wr': current_wr}
            
            msg = bot.send_message(chat_id, "Введите количество сыгранных матчей:")
            bot.register_next_step_handler(msg, process_matches, bot)
            
        except ValueError:
            msg = bot.reply_to(message, "Пожалуйста, введите корректный процент (0-100)")
            bot.register_next_step_handler(msg, process_current_winrate, bot)

    def process_matches(message, bot):
        try:
            matches = int(message.text)
            if matches < 0:
                raise ValueError
            
            chat_id = message.chat.id
            user_data[chat_id]['matches'] = matches
            
            msg = bot.send_message(chat_id, "Введите ожидаемый винрейт в будущих играх (0-100%):")
            bot.register_next_step_handler(msg, process_expected_winrate, bot)
            
        except ValueError:
            msg = bot.reply_to(message, "Пожалуйста, введите корректное количество матчей")
            bot.register_next_step_handler(msg, process_matches, bot)

    def process_expected_winrate(message, bot):
        try:
            expected_wr = float(message.text)
            if not 0 <= expected_wr <= 100:
                raise ValueError
            
            chat_id = message.chat.id
            user_data[chat_id]['expected_wr'] = expected_wr
            
            msg = bot.send_message(chat_id, "Введите желаемый итоговый винрейт (0-100%):")
            bot.register_next_step_handler(msg, calculate_result, bot)
            
        except ValueError:
            msg = bot.reply_to(message, "Пожалуйста, введите корректный процент (0-100)")
            bot.register_next_step_handler(msg, process_expected_winrate, bot)

    def calculate_result(message, bot):
        try:
            desired_wr = float(message.text)
            if not 0 <= desired_wr <= 100:
                raise ValueError
            
            chat_id = message.chat.id
            data = user_data[chat_id]
            
            games_needed = calculate_additional_matches(
                data['current_wr'],
                data['matches'],
                data['expected_wr'],
                desired_wr
            )
            
            if games_needed == -1:
                response = (
                    "Невозможно достичь желаемого винрейта с текущими параметрами.\n"
                    "Убедитесь, что желаемый винрейт не превышает ожидаемый."
                )
            else:
                response = (
                    f"Текущий винрейт: {data['current_wr']}%\n"
                    f"Сыграно матчей: {data['matches']}\n"
                    f"Ожидаемый винрейт: {data['expected_wr']}%\n"
                    f"Желаемый винрейт: {desired_wr}%\n\n"
                    f"Необходимо сыграть еще {games_needed} матчей"
                )
            
            bot.send_message(chat_id, response)
            user_data.pop(chat_id, None)  # Очищаем данные пользователя
            
        except ValueError:
            msg = bot.reply_to(message, "Пожалуйста, введите корректный процент (0-100)")
            bot.register_next_step_handler(msg, calculate_result, bot)

    return winrate_calculator