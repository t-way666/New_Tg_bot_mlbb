from telebot import types
import logging
from config.constants import RANKS, MYTHIC_GRADES, get_rank_and_level, get_total_stars_for_rank

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
                "❗ Пожалуйста, вводите все значения — от этого зависит результат подсчетов\n\n"
                "С какого ранга вы начинали сезон?"
            )
        else:
            # Для текущего или целевого ранга показываем все
            ranks_to_show = RANKS
            # Добавим также кнопки для «мифических» подрангов (если нужно)
            for threshold, rank_name in MYTHIC_GRADES.items():
                if rank_name != "Мифический":
                    btn = types.InlineKeyboardButton(rank_name, callback_data=f"{step}::{rank_name}")
                    markup.add(btn)
            
            if step == "current_rank":
                message_text = "На каком ранге вы сейчас находитесь?"
            else:
                message_text = "Какой ранг вы хотите достичь?"

        for rank in ranks_to_show:
            btn = types.InlineKeyboardButton(rank['name'], callback_data=f"{step}::{rank['name']}")
            markup.add(btn)
        
        bot.send_message(chat_id, message_text, reply_markup=markup)

    def show_level_keyboard(chat_id, rank_name, level_type="start"):
        """Создает клавиатуру с уровнями"""
        markup = types.InlineKeyboardMarkup(row_width=5)
        rank_data = next((r for r in RANKS if r['name'] == rank_name), None)
        
        if level_type == "start":
            message_text = f"С какого уровня ранга {rank_name} вы начали?"
        elif level_type == "current":
            message_text = f"Какой уровень ранга {rank_name} у вас сейчас?"
        else:
            message_text = f"Какой уровень ранга {rank_name} вы хотите достичь?"

        if rank_data:
            for level in range(1, rank_data['levels'] + 1):
                btn = types.InlineKeyboardButton(str(level), callback_data=f"level::{level}")
                markup.add(btn)
            
            # Кнопка "Не помню" только для начального уровня (или по вашему желанию)
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
        """Точка входа при команде /season_progress"""
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
        """Обрабатывает выбор ранга (начальный, текущий или целевой)."""
        try:
            chat_id = call.message.chat.id
            step, rank = call.data.split("::")

            # Сохраняем в user_data соответствующий ключ
            if step == "start_rank":
                user_data[chat_id]['start_rank'] = rank
                user_data[chat_id]['current_step'] = 'start'
                
                # Если это не Мифик — спрашиваем уровень
                if rank in [r['name'] for r in RANKS if r['name'] != "Мифический"]:
                    show_level_keyboard(chat_id, rank, "start")
                else:
                    # Если вдруг Mythic с самого начала (нечасто, но теоретически возможно)
                    bot.send_message(chat_id, "Сколько матчей вы уже сыграли в этом сезоне? (в рейтинговом режиме)")
                    bot.register_next_step_handler(call.message, process_games_played)

            elif step == "current_rank":
                user_data[chat_id]['current_rank'] = rank
                user_data[chat_id]['current_step'] = 'current'
                
                if rank in [r['name'] for r in RANKS if r['name'] != "Мифический"]:
                    show_level_keyboard(chat_id, rank, "current")
                else:
                    bot.send_message(chat_id, "Сколько мифических звезд у вас сейчас?")
                    bot.register_next_step_handler(call.message, process_mythic_stars)

            elif step == "target_rank":
                user_data[chat_id]['target_rank'] = rank
                user_data[chat_id]['current_step'] = 'target'
                
                # Если целевой ранг не Мифический — уточняем уровень
                if rank in [r['name'] for r in RANKS if r['name'] != "Мифический"]:
                    show_level_keyboard(chat_id, rank, "target")
                else:
                    # Если целевой ранг — Мифик, запросим позже количество звезд, если нужно
                    bot.send_message(chat_id, "Целевой ранг — Мифический. Сколько мифических звезд вы хотите набрать?")
                    bot.register_next_step_handler(call.message, process_target_mythic_stars)

            bot.answer_callback_query(call.id)
            bot.delete_message(chat_id, call.message.message_id)
            
        except Exception as e:
            logger.error(f"Ошибка в обработке выбора ранга: {e}")
            bot.answer_callback_query(call.id, "Произошла ошибка. Попробуйте снова.")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("level::"))
    def handle_level_selection(call):
        """Обрабатывает выбор уровня (1,2,3...) после выбора ранга."""
        try:
            chat_id = call.message.chat.id
            level = call.data.split("::")[1]
            
            # current_step: 'start', 'current' или 'target'
            step = user_data[chat_id].get('current_step', 'start')

            if level == "dont_remember":
                # Если пользователь не помнит уровень, ставим условно 1 уровень и 0 звезд
                user_data[chat_id][f'{step}_level'] = 1
                user_data[chat_id][f'{step}_stars'] = 0

                if step == 'start':
                    bot.send_message(chat_id, "Сколько матчей вы уже сыграли в этом сезоне?")
                    bot.register_next_step_handler(call.message, process_games_played)
                elif step == 'current':
                    # Переходим к выбору целевого ранга
                    show_rank_keyboard(chat_id, "target_rank")
                elif step == 'target':
                    # Здесь можно сразу перейти к расчетам или к вводу мифических звезд
                    bot.send_message(chat_id, "Хорошо. Считаем, что начинаете с 1 уровня целевого ранга без звёзд.")
                    # Допустим, сразу завершаем или просим что-то ещё
                    bot.send_message(chat_id, "Теперь введите предполагаемый винрейт для оставшихся игр (0-100):")
                    bot.register_next_step_handler(call.message, process_expected_winrate)

            else:
                user_data[chat_id][f'{step}_level'] = int(level)
                # Определяем имя выбранного ранга
                rank_name = user_data[chat_id][f'{step}_rank']
                show_stars_keyboard(chat_id, rank_name, level)

            bot.answer_callback_query(call.id)
            bot.delete_message(chat_id, call.message.message_id)
            
        except Exception as e:
            logger.error(f"Ошибка при обработке выбора уровня: {e}")
            bot.answer_callback_query(call.id, "Произошла ошибка. Попробуйте снова.")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("stars::"))
    def handle_stars_selection(call):
        """Обрабатывает выбор количества звёзд."""
        try:
            chat_id = call.message.chat.id
            stars_value = call.data.split("::")[1]
            step = user_data[chat_id]['current_step']  # 'start', 'current' или 'target'

            if stars_value == "dont_remember":
                user_data[chat_id][f'{step}_stars'] = 0
            else:
                user_data[chat_id][f'{step}_stars'] = int(stars_value)

            # Дальше логика в зависимости от шага
            if step == 'start':
                bot.send_message(chat_id, "Сколько матчей вы уже сыграли в этом сезоне?")
                bot.register_next_step_handler(call.message, process_games_played)
            elif step == 'current':
                # Переходим к целевому рангу
                show_rank_keyboard(chat_id, "target_rank")
            elif step == 'target':
                # Можно переходить к вводу винрейта и финальным расчетам
                bot.send_message(chat_id, "Теперь введите предполагаемый винрейт для оставшихся игр (0-100):")
                bot.register_next_step_handler(call.message, process_expected_winrate)

            bot.answer_callback_query(call.id)
            bot.delete_message(chat_id, call.message.message_id)

        except Exception as e:
            logger.error(f"Ошибка при обработке выбора звёзд: {e}")
            bot.answer_callback_query(call.id, "Произошла ошибка. Попробуйте снова.")

    def process_games_played(message):
        """Обработка ввода количества сыгранных матчей в сезоне."""
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
        """Обработка ввода текущего винрейта."""
        try:
            cleaned_text = message.text.replace('%', '').strip()
            winrate = float(cleaned_text)
            if not 0 <= winrate <= 100:
                raise ValueError
                
            chat_id = message.chat.id
            user_data[chat_id]['winrate'] = winrate
            
            # Теперь спрашиваем текущий ранг
            bot.send_message(chat_id, "Выберите ваш ТЕКУЩИЙ ранг:")
            show_rank_keyboard(chat_id, "current_rank")
            
        except ValueError:
            msg = bot.reply_to(message, "Пожалуйста, введите число от 0 до 100")
            bot.register_next_step_handler(msg, process_winrate)

    def process_mythic_stars(message):
        """Обработка ввода мифических звезд (для текущего ранга)."""
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

    def process_target_mythic_stars(message):
        """Если целевой ранг — Мифик, обрабатываем ввод предполагаемого числа звёзд."""
        try:
            stars = int(message.text)
            if stars < 0:
                raise ValueError
            
            chat_id = message.chat.id
            user_data[chat_id]['target_stars'] = stars
            
            # Далее спрашиваем винрейт
            bot.send_message(
                chat_id,
                "Как вы думаете, какой винрейт (предположительно) у вас будет в дополнительных играх? (от 0 до 100)"
            )
            bot.register_next_step_handler(message, process_expected_winrate)

        except ValueError:
            msg = bot.reply_to(message, "Пожалуйста, введите корректное число звёзд.")
            bot.register_next_step_handler(msg, process_target_mythic_stars)

    def process_expected_winrate(message):
        """Обработка ввода предполагаемого винрейта в будущих играх."""
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
        """Обработка ввода целевого винрейта (до конца сезона)."""
        try:
            target_wr = float(message.text.replace('%', '').strip())
            if not 0 <= target_wr <= 100:
                raise ValueError
            
            chat_id = message.chat.id
            user_data[chat_id]['target_winrate'] = target_wr
            
            # Рассчитываем необходимое количество матчей
            needed_games = calculate_needed_games(user_data[chat_id])
            
            # Формируем итоговое сообщение
            result = format_final_message(user_data[chat_id], needed_games)
            
            bot.send_message(chat_id, result)
            
            # Очищаем данные пользователя после завершения
            if chat_id in user_data:
                del user_data[chat_id]
                
        except ValueError:
            msg = bot.reply_to(message, "Пожалуйста, введите число от 0 до 100")
            bot.register_next_step_handler(msg, process_target_winrate)

    def format_final_message(u_data, needed_games):
        """Формируем итоговое сообщение для пользователя."""
        current_info = ""
        if 'current_level' in u_data:
            current_info = f"уровень {u_data['current_level']}"
        
        target_info = ""
        if 'target_level' in u_data:
            target_info = f"уровень {u_data['target_level']}"
        
        start_rank_str = u_data.get('start_rank', 'Неизвестно')
        current_rank_str = u_data.get('current_rank', 'Неизвестно')
        target_rank_str = u_data.get('target_rank', '???')

        return (
            "🎮 Итак. Учитывая введенные значения:\n\n"
            f"📈 Начинали сезон с {start_rank_str}\n"
            f"🎯 Сыграли {u_data.get('games_played', 0)} матчей с винрейтом {u_data.get('winrate', 0)}%\n"
            f"🏆 Сейчас вы на {current_rank_str} {current_info}\n"
            f"✨ Цель: {target_rank_str} {target_info}\n\n"
            f"Чтобы достичь желаемого ранга, вам нужно сыграть примерно {needed_games} матчей "
            f"с текущим (или ожидаемым) винрейтом {u_data.get('winrate', 0)}%\n\n"
            "🍀 Удачи в достижении цели! 🌟"
        )

    def calculate_needed_games(u_data):
        """
        Пример простой логики расчета необходимого количества матчей для достижения целевого ранга.
        Здесь вы можете расширять логику в зависимости от того,
        как именно в MLBB рассчитываются переходы по звездам и т.д.
        """
        try:
            current_stars = u_data.get('current_stars', 0)
            target_stars = u_data.get('target_stars', 0)
            winrate = u_data.get('winrate', 50) / 100  # переводим в десятичную дробь
            
            if current_stars >= target_stars:
                return 0
                
            stars_needed = target_stars - current_stars
            
            # Простейшая формула: при 50% винрейте игрок не двигается (1 победа +1 звезда, 1 поражение -1 звезда)
            # stars_needed = games * (2*winrate - 1)
            if winrate <= 0.5:
                return "невозможно (винрейт слишком низкий)"
                
            avg_stars_per_game = (2 * winrate - 1)
            
            if avg_stars_per_game <= 0:
                return "невозможно с текущим винрейтом"
                
            games_needed = int(stars_needed / avg_stars_per_game) + 1
            return games_needed

        except Exception as e:
            logger.error(f"Ошибка при расчете необходимых игр: {e}")
            return "неопределенное количество"

    return start_season_progress
