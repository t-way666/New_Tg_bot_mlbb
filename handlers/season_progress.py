from telebot import types
import logging
from config.constants import RANKS, MYTHICAL_RANKS, get_rank_and_level, get_total_stars_for_rank  # Изменен импорт

# Настраиваем логирование
logger = logging.getLogger(__name__)

def send_season_progress(bot):
    user_data = {}

    def show_rank_keyboard(chat_id, step):
        """Создает клавиатуру с рангами"""
        markup = types.InlineKeyboardMarkup(row_width=2)
        
        # Для начального ранга показываем только до Легенды
        if step == "start_rank":
            ranks_to_show = [rank for rank in RANKS if rank['name'] != "Мифический"]
            message_text = (
                "❗ Пожалуйста, вводите все значения - от этого зависит результат подсчетов\n\n"
                "С какого ранга вы начинали сезон?"
            )
        else:
            # Для текущего ранга показываем все
            ranks_to_show = RANKS
            for threshold, rank_name in MYTHICAL_RANKS.items():
                if rank_name != "Мифический":
                    btn = types.InlineKeyboardButton(rank_name, callback_data=f"{step}::{rank_name}")
                    markup.add(btn)
            message_text = "На каком ранге вы сейчас находитесь?"

        for rank in ranks_to_show:
            btn = types.InlineKeyboardButton(rank['name'], callback_data=f"{step}::{rank['name']}")
            markup.add(btn)
        
        bot.send_message(chat_id, message_text, reply_markup=markup)

    def show_level_keyboard(chat_id, rank_name, level_type="start"):
        """Создает клавиатуру с уровнями"""
        markup = types.InlineKeyboardMarkup(row_width=5)
        rank_data = next((r for r in RANKS if r['name'] == rank_name), None)
        
        message_text = f"С какого уровня ранга {rank_name} вы начали?" if level_type == "start" else f"Какой уровень ранга {rank_name}?"
        
        if rank_data:
            for level in range(1, rank_data['levels'] + 1):
                btn = types.InlineKeyboardButton(str(level), callback_data=f"level::{level}")
                markup.add(btn)
            
            # Кнопка "Не помню" только для начального уровня
            if level_type == "start":
                btn_dont_remember = types.InlineKeyboardButton("Не помню", callback_data="level::dont_remember")
                markup.add(btn_dont_remember)
            
            bot.send_message(chat_id, message_text, reply_markup=markup)

    def show_stars_keyboard(chat_id, rank_name, level):
        """Создает клавиатуру для выбора звезд"""
        markup = types.InlineKeyboardMarkup(row_width=5)
        rank_data = next((r for r in RANKS if r['name'] == rank_name), None)
        
        if rank_data:
            for stars in range(1, rank_data['stars_per_level'] + 1):
                btn = types.InlineKeyboardButton(str(stars), callback_data=f"stars::{stars}")
                markup.add(btn)
            
            btn_dont_remember = types.InlineKeyboardButton("Не помню", callback_data="stars::dont_remember")
            markup.add(btn_dont_remember)
            
            message_text = f"Сколько звезд у вас было в {level} уровне ранга {rank_name}?"
            bot.send_message(chat_id, message_text, reply_markup=markup)

    @bot.message_handler(commands=['season_progress'])
    def start_season_progress(message):
        try:
            chat_id = message.chat.id
            user_data[chat_id] = {}  # Инициализируем данные пользователя
            
            bot.send_message(
                chat_id,
                "Давайте посчитаем ваш прогресс в сезоне и сколько матчей нужно до цели.\n"
                "С какого ранга вы начинали сезон?"
            )
            show_rank_keyboard(chat_id, "start_rank")
            
        except Exception as e:
            logger.error(f"Ошибка в season_progress: {e}")
            bot.reply_to(message, "Произошла ошибка. Попробуйте позже.")

    @bot.callback_query_handler(func=lambda call: call.data.startswith(("start_rank::", "current_rank::", "target_rank::")))
    def handle_rank_selection(call):
        try:
            chat_id = call.message.chat.id
            step, rank = call.data.split("::")
            user_data[chat_id][step.replace('_rank', '')] = rank
            
            if step == "start_rank":
                if rank in [r['name'] for r in RANKS if r['name'] != "Мифический"]:
                    show_level_keyboard(chat_id, rank, "start")
                else:
                    bot.send_message(chat_id, "Сколько матчей вы уже сыграли в этом сезоне? (в рейтинговом режиме)")
                    bot.register_next_step_handler(call.message, process_games_played)
            elif step == "current_rank":
                if rank in [r['name'] for r in RANKS if r['name'] != "Мифический"]:
                    show_level_keyboard(chat_id, rank, "current")
                else:
                    bot.send_message(chat_id, "Сколько мифических звезд у вас сейчас?")
                    bot.register_next_step_handler(call.message, process_mythic_stars)
            
            bot.answer_callback_query(call.id)
            bot.delete_message(chat_id, call.message.message_id)
            
        except Exception as e:
            logger.error(f"Ошибка в обработке выбора ранга: {e}")
            bot.answer_callback_query(call.id, "Произошла ошибка. Попробуйте снова.")

    @bot.callback_query_handler(func=lambda call: call.data.endswith("::dont_remember"))
    def handle_dont_remember(call):
        try:
            chat_id = call.message.chat.id
            step = call.data.split("::")[0]
            
            if step == "start_rank":
                user_data[chat_id]['start_rank'] = None
                user_data[chat_id]['start_level'] = 0
                user_data[chat_id]['start_stars'] = 0
                bot.send_message(chat_id, "Хорошо, будем считать с нуля. Сколько матчей вы уже сыграли в этом сезоне?")
                bot.register_next_step_handler(call.message, process_games_played)
            elif step == "level":
                user_data[chat_id]['start_level'] = 0
                user_data[chat_id]['start_stars'] = 0
                bot.send_message(chat_id, "Хорошо, будем считать с начала уровня. Сколько матчей вы уже сыграли в этом сезоне?")
                bot.register_next_step_handler(call.message, process_games_played)
                
            bot.answer_callback_query(call.id)
            bot.delete_message(chat_id, call.message.message_id)
            
        except Exception as e:
            logger.error(f"Ошибка при обработке 'не помню': {e}")
            bot.answer_callback_query(call.id, "Произошла ошибка. Попробуйте снова.")

    def process_games_played(message):
        try:
            games = int(message.text)
            if games < 0:
                raise ValueError
                
            chat_id = message.chat.id
            user_data[chat_id]['games_played'] = games
            
            bot.send_message(chat_id, "Какой у вас текущий винрейт? (от 0 до 100)")
            bot.register_next_step_handler(message, process_winrate)
            
        except ValueError:
            bot.reply_to(message, "Пожалуйста, введите корректное число матчей.")
            bot.register_next_step_handler(message, process_games_played)

    def process_winrate(message):
        try:
            # Удаляем знак процента, если пользователь его ввел
            cleaned_text = message.text.replace('%', '').strip()
            winrate = float(cleaned_text)
            if not 0 <= winrate <= 100:
                raise ValueError
                
            chat_id = message.chat.id
            user_data[chat_id]['winrate'] = winrate
            
            bot.send_message(
                chat_id,
                "Выберите ваш ТЕКУЩИЙ ранг:"
            )
            show_rank_keyboard(chat_id, "current_rank")
            
        except ValueError:
            msg = bot.reply_to(
                message, 
                "Пожалуйста, введите число от 0 до 100"
            )
            bot.register_next_step_handler(msg, process_winrate)

    def process_mythic_stars(message):
        try:
            stars = int(message.text)
            if stars < 0:
                raise ValueError
            
            chat_id = message.chat.id
            user_data[chat_id]['current_stars'] = stars
            
            bot.send_message(
                chat_id,
                "Как вы думаете, какой винрейт (предположительно) у вас будет в дополнительных играх? (от 0 до 100)"
            )
            bot.register_next_step_handler(message, process_expected_winrate)
            
        except ValueError:
            msg = bot.reply_to(message, "Пожалуйста, введите корректное число звезд.")
            bot.register_next_step_handler(msg, process_mythic_stars)

    def process_expected_winrate(message):
        try:
            winrate = float(message.text.replace('%', '').strip())
            if not 0 <= winrate <= 100:
                raise ValueError
            
            chat_id = message.chat.id
            user_data[chat_id]['expected_winrate'] = winrate
            
            bot.send_message(
                chat_id,
                "Какого винрейта в конце концов вы хотите добиться? (от 0 до 100)"
            )
            bot.register_next_step_handler(message, process_target_winrate)
            
        except ValueError:
            msg = bot.reply_to(message, "Пожалуйста, введите число от 0 до 100")
            bot.register_next_step_handler(msg, process_expected_winrate)

    def process_target_winrate(message):
        try:
            target_wr = float(message.text.replace('%', '').strip())
            if not 0 <= target_wr <= 100:
                raise ValueError
            
            chat_id = message.chat.id
            user_data[chat_id]['target_winrate'] = target_wr
            
            # Формируем итоговое сообщение
            result = (
                "🎮 Итак. Учитывая введенные значения (надеюсь вы не сливались, хаха), вы:\n\n"
                f"📈 Начинали сезон с {user_data[chat_id]['start_rank']}"
                f" (уровень {user_data[chat_id].get('start_level', '0')}, "
                f"звезд: {user_data[chat_id].get('start_stars', '0')})\n"
                f"🎯 Сыграли {user_data[chat_id]['games_played']} матчей "
                f"с винрейтом {user_data[chat_id]['winrate']}%\n"
                f"🏆 Сейчас вы достигли {user_data[chat_id]['current_rank']}"
            )
            
            # Добавляем информацию о текущем уровне/звездах
            if 'current_level' in user_data[chat_id]:
                result += f" (уровень {user_data[chat_id]['current_level']})"
            if 'current_stars' in user_data[chat_id]:
                result += f" ({user_data[chat_id]['current_stars']} звезд)"
            
            # Рассчитываем необходимое количество матчей
            # Здесь должна быть ваша логика расчета
            needed_games = calculate_needed_games(user_data[chat_id])
            
            result += (
                f"\n\n✨ Чтобы достичь желаемого винрейта {target_wr}%, "
                f"вам нужно сыграть примерно {needed_games} матчей "
                f"с винрейтом {user_data[chat_id]['expected_winrate']}%\n\n"
                "🍀 Надеюсь, вы достигните своей цели! Желаю вам хороших игр и тиммейтов! 🌟"
            )
            
            bot.send_message(chat_id, result)
            
        except ValueError:
            msg = bot.reply_to(message, "Пожалуйста, введите число от 0 до 100")
            bot.register_next_step_handler(msg, process_target_winrate)

    def calculate_needed_games(user_data):
        """
        Рассчитывает необходимое количество игр для достижения целевого винрейта
        
        Args:
            user_data (dict): Словарь с данными пользователя
            Содержит:
            - games_played: количество сыгранных игр
            - winrate: текущий винрейт
            - expected_winrate: ожидаемый винрейт в будущих играх
            - target_winrate: целевой винрейт
        
        Returns:
            int: Количество необходимых игр
        """
        try:
            current_games = user_data['games_played']
            current_wr = user_data['winrate']
            expected_wr = user_data['expected_winrate']
            target_wr = user_data['target_winrate']
            
            # Текущее количество побед
            current_wins = (current_games * current_wr) / 100
            
            # Формула для расчета необходимых игр:
            # (target_wr * (current_games + x) = (current_wins + expected_wr * x)
            # Где x - количество необходимых игр
            
            if expected_wr == target_wr:
                return "∞" if current_wr != target_wr else "0"
            
            needed_games = (
                (target_wr * current_games - 100 * current_wins) / 
                (expected_wr - target_wr)
            )
            
            return max(0, round(needed_games))
            
        except (KeyError, ZeroDivisionError):
            return "N/A"  # В случае ошибки или отсутствия данных

    return start_season_progress