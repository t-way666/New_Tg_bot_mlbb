from telebot import types
import logging
import sys
from pathlib import Path

# Добавляем корневую директорию в PYTHONPATH
root_dir = Path(__file__).parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

from config.constants import RANKS, MYTHICAL_RANKS, get_total_stars_for_rank

# Настраиваем логирование
logger = logging.getLogger(__name__)

def send_my_stars(bot):
    user_data = {}

    def show_rank_keyboard(chat_id):
        """Создает клавиатуру с рангами"""
        markup = types.InlineKeyboardMarkup(row_width=2)
        for rank in RANKS:
            callback_data = f"rank::{rank['name']}"
            btn = types.InlineKeyboardButton(rank['name'], callback_data=callback_data)
            markup.add(btn)
        
        # Добавляем мифические ранги
        for threshold, rank_name in MYTHICAL_RANKS.items():
            if rank_name != "Мифический":  # Исключаем дубликат
                callback_data = f"rank::{rank_name}"
                btn = types.InlineKeyboardButton(rank_name, callback_data=callback_data)
                markup.add(btn)
        
        bot.send_message(
            chat_id,
            "Выберите ваш текущий ранг:",
            reply_markup=markup
        )

    @bot.message_handler(commands=['my_stars'])
    def start_my_stars(message):
        try:
            chat_id = message.chat.id
            user_data[chat_id] = {}
            show_rank_keyboard(chat_id)
        except Exception as e:
            logger.error(f"Ошибка в my_stars: {e}")
            bot.reply_to(message, "Произошла ошибка. Попробуйте позже.")

    # ... добавить остальные обработчики ...

    return start_my_stars