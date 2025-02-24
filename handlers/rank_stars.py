from telebot import types
import logging
from config.constants import RANKS, MYTHIC_GRADES, get_total_stars_for_rank, get_rank_and_level

logger = logging.getLogger(__name__)

def send_rank_stars(bot):
    user_data = {}

    def show_initial_keyboard(chat_id):
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn_rank = types.InlineKeyboardButton("Ранг", callback_data="calc::rank")
        btn_stars = types.InlineKeyboardButton("Звезды", callback_data="calc::stars")
        markup.add(btn_rank, btn_stars)
        
        message_text = (
            "Что мы хотим просчитать?\n\n"
            "1. Определить ранг ориентируясь на общее количество звезд\n"
            "2. Определить общего количества звезд ориентируясь на ранг\n\n"
            "❗ Учет ведется начиная с минимального ранга - Воин, уровень 3, 0 звезд"
        )
        
        bot.send_message(chat_id, message_text, reply_markup=markup)

    def show_ranks_keyboard(chat_id):
        markup = types.InlineKeyboardMarkup(row_width=2)
        for rank in RANKS:
            btn = types.InlineKeyboardButton(rank, callback_data=f"rank::{rank}")
            markup.add(btn)
        bot.send_message(chat_id, "Выберите ранг:", reply_markup=markup)

    def show_levels_keyboard(chat_id, rank):
        if rank == "Мифический":
            bot.send_message(chat_id, "Сколько у вас мифических звезд?")
            bot.register_next_step_handler(bot.get_chat(chat_id), calculate_mythic_stars)
        else:
            levels = range(1, 6) if rank != "Воин" else range(3, 6)
            markup = types.InlineKeyboardMarkup(row_width=3)
            for level in levels:
                btn = types.InlineKeyboardButton(str(level), callback_data=f"level::{level}")
                markup.add(btn)
            bot.send_message(chat_id, f"Выберите уровень для ранга {rank}:", reply_markup=markup)

    @bot.message_handler(commands=['rank_stars'])
    def start_rank_stars(message):
        try:
            chat_id = message.chat.id
            user_data[chat_id] = {}
            show_initial_keyboard(chat_id)
        except Exception as e:
            logger.error(f"Ошибка в rank_stars: {e}")
            bot.reply_to(message, "Произошла ошибка. Попробуйте позже.")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("calc::"))
    def handle_calc_choice(call):
        try:
            chat_id = call.message.chat.id
            choice = call.data.split("::")[1]
            user_data[chat_id] = {'choice': choice}
            
            if choice == "rank":
                bot.send_message(chat_id, "Введите общее количество звезд:")
                bot.register_next_step_handler(call.message, calculate_rank)
            else:  # choice == "stars"
                show_ranks_keyboard(chat_id)

            bot.answer_callback_query(call.id)
            bot.delete_message(chat_id, call.message.message_id)
        except Exception as e:
            logger.error(f"Ошибка при обработке выбора: {e}")
            bot.answer_callback_query(call.id, "Произошла ошибка. Попробуйте снова.")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("rank::"))
    def handle_rank_choice(call):
        try:
            chat_id = call.message.chat.id
            rank = call.data.split("::")[1]
            user_data[chat_id]['rank'] = rank
            show_levels_keyboard(chat_id, rank)
            bot.answer_callback_query(call.id)
            bot.delete_message(chat_id, call.message.message_id)
        except Exception as e:
            logger.error(f"Ошибка при выборе ранга: {e}")
            bot.answer_callback_query(call.id, "Произошла ошибка. Попробуйте снова.")

    @bot.callback_query_handler(func=lambda call: call.data.startswith(("level::", "mythic_type::")))
    def handle_level_choice(call):
        try:
            chat_id = call.message.chat.id
            data_type, value = call.data.split("::")
            
            if data_type == "mythic_type":
                user_data[chat_id]['mythic_type'] = value
                bot.send_message(chat_id, "Введите количество мифических звезд:")
                bot.register_next_step_handler(call.message, calculate_mythic_stars)
            else:
                user_data[chat_id]['level'] = int(value)
                rank = user_data[chat_id]['rank']
                level = int(value)
                total_stars = get_total_stars_for_rank(rank, level)
                response = f"Для достижения {rank} {level} требуется всего {total_stars} звезд"
                bot.send_message(chat_id, response)

            bot.answer_callback_query(call.id)
            bot.delete_message(chat_id, call.message.message_id)
        except Exception as e:
            logger.error(f"Ошибка при выборе уровня: {e}")
            bot.answer_callback_query(call.id, "Произошла ошибка. Попробуйте снова.")

    def calculate_rank(message):
        try:
            stars = int(message.text)
            if stars < 0:
                bot.reply_to(message, "Количество звезд не может быть отрицательным.")
                return
            rank, mythic_stars = get_rank_and_level(stars)
            if "Мифический" in rank:
                # Если просто Мифический (0-24 звезды)
                if rank == "Мифический":
                    response = f"С {stars} звездами ваш ранг: Мифический ({mythic_stars} звезд)"
                else:  # Если есть градация (Честь/Слава/Бессмертный)
                    response = f"С {stars} звездами ваш ранг: {rank} ({mythic_stars} звезд)"
            else:
                response = f"С {stars} звездами ваш ранг: {rank} {mythic_stars}"
            bot.reply_to(message, response)
        except ValueError:
            bot.reply_to(message, "Пожалуйста, введите корректное число звезд (целое положительное число).")
        except Exception as e:
            logger.error(f"Ошибка при расчете ранга: {e}")
            bot.reply_to(message, "Произошла ошибка при расчете.")

    def calculate_mythic_stars(message):
        try:
            chat_id = message.chat.id
            mythic_stars = int(message.text)
            if mythic_stars < 0:
                bot.reply_to(message, "Количество мифических звезд не может быть отрицательным.")
                return
            
            total_stars = get_total_stars_for_rank("Мифический", 1, mythic_stars)
            grade = ""
            for g, (min_s, max_s) in MYTHIC_GRADES.items():
                if min_s <= mythic_stars <= max_s:
                    grade = g
                    break
                
            rank_name = f"Мифический{' ' + grade if grade else ''}"
            response = f"С {mythic_stars} звездами ваш ранг: {rank_name}\nВсего звезд: {total_stars}"
            bot.send_message(chat_id, response)
        except ValueError:
            bot.reply_to(message, "Пожалуйста, введите корректное число мифических звезд.")
        except Exception as e:
            logger.error(f"Ошибка при расчете мифических звезд: {e}")
            bot.reply_to(message, "Произошла ошибка при расчете.")

    return start_rank_stars