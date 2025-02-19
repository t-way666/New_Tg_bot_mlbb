from telebot import types
import logging
from config.constants import get_rank_and_level  # Изменен импорт на абсолютный

# Настраиваем логирование
logger = logging.getLogger(__name__)

def send_rank(bot):
    @bot.message_handler(commands=['rank'])
    def send_rank_message(message):
        try:
            msg = bot.send_message(
                message.chat.id,
                "Введите общее количество звёзд (целое число ≥ 0), "
                "чтобы узнать ваш ранг:"
            )
            bot.register_next_step_handler(msg, process_rank_stars)
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения: {e}")
            bot.reply_to(message, "Произошла ошибка. Попробуйте позже.")

    def process_rank_stars(message):
        try:
            if message.text.startswith('/'):
                bot.reply_to(message, "Операция отменена. Используйте /help для списка команд.")
                return

            stars = int(message.text.strip())
            if stars < 0:
                raise ValueError("Количество звёзд не может быть отрицательным")

            rank_name, level, stars_in_level = get_rank_and_level(stars)
            
            if rank_name is None:
                raise ValueError("Ошибка при расчете ранга")

            if level is not None:
                response = (
                    f"🏆 Ваш ранг: {rank_name}\n"
                    f"📊 Уровень: {level}\n"
                    f"⭐ Звёзд в уровне: {stars_in_level}"
                )
            else:
                response = f"🏆 Ранг: {rank_name}\n⭐ Количество звёзд: {stars_in_level}"

            bot.reply_to(message, response)

        except ValueError as e:
            bot.reply_to(message, "Пожалуйста, введите корректное целое число ≥ 0")
        except Exception as e:
            logger.error(f"Ошибка при обработке количества звёзд: {e}")
            bot.reply_to(message, "Произошла ошибка. Попробуйте позже.")

    return send_rank_message