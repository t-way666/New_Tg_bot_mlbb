import time

def send_start(bot):
    @bot.message_handler(commands=['start'])
    def send_start_message(message):
        user_first_name = message.from_user.first_name
        
        # Приветствие
        greeting = f"Привет, {user_first_name}\nДобро пожаловать в нашего телеграм бота.\nВот команды, которые я понимаю:\n\n"
        commands = [
            "/start — Начать или перезапустить бота",
            "/armor_and_resistance — Калькулятор защиты и снижения урона",
            "/help — Помощь",
            "/my_stars — Узнать общее количество звёзд по рангу",
            "/rank — Определить ваш ранг по количеству звёзд",
            "/season_progress — Посчитать, сколько ещё игр нужно до желаемого ранга (учитывая начало сезона)",
            "/winrate_correction — Корректировка винрейта"
        ]

        # Отправляем приветствие
        msg = bot.send_message(message.chat.id, greeting)
        time.sleep(0.3)  # Пауза после приветствия

        # Добавляем команды по одной
        current_text = greeting
        for cmd in sorted(commands):  # Сортируем команды по алфавиту (кроме /start)
            if not cmd.startswith('/start'):
                current_text += cmd + "\n\n"
                try:
                    bot.edit_message_text(
                        chat_id=message.chat.id,
                        message_id=msg.message_id,
                        text=current_text
                    )
                    time.sleep(0.1)  # Пауза между добавлением команд
                except Exception as e:
                    if "message is not modified" not in str(e):
                        print(f"Error: {e}")
                        
    return send_start_message