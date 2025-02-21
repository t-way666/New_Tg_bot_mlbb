import sqlite3
from telebot import types
import logging
import os

logger = logging.getLogger(__name__)

# Обновленная карта характеристик на основе CSV
CHARACTERISTICS_MAP = {
    'hp': ('❤️ ОЗ', 'ОЗ'),
    'hp_regen': ('💗 Реген ОЗ', 'реген_ОЗ'),
    'mana': ('💙 Мана', 'мана/энергия'),
    'mana_regen': ('💠 Реген маны', 'реген_маны/энергии'),
    'phys_attack': ('⚔️ Физ.атака', 'физ_атака'),
    'phys_def': ('🛡️ Физ.защита', 'физ_защита'),
    'mag_def': ('🔮 Маг.защита', 'маг_защита'),
    'attack_speed': ('⚡ Скор.атаки', 'скорость_атаки'),
    'move_speed': ('👟 Скор.движения', 'скорость_передвижения')
}

def check_db_structure():
    """Функция для проверки структуры базы данных"""
    try:
        conn = sqlite3.connect('characters.db')
        cursor = conn.cursor()
        
        # Получаем информацию о столбцах таблицы
        cursor.execute("PRAGMA table_info(heroes)")
        columns = cursor.fetchall()
        
        print("Структура таблицы heroes:")
        for column in columns:
            print(f"Column: {column[1]}, Type: {column[2]}")
            
        conn.close()
        return columns
        
    except Exception as e:
        logger.error(f"Ошибка при проверке структуры БД: {e}")
        return None

# Запустите эту функцию перед реализацией основного функционала
columns = check_db_structure()

def get_heroes_by_stat(stat, level):
    """Получение отсортированного списка героев по характеристике"""
    try:
        # Используем правильный путь к базе данных
        db_path = os.path.join(os.path.dirname(__file__), '..', 'db', 'characters.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Определяем, растет ли характеристика с уровнем
        growing_stats = {
            'ОЗ': ('ОЗ', 'прирост_ОЗ'),
            'реген_ОЗ': ('реген_ОЗ', 'прирост_реген_ОЗ'),
            'мана/энергия': ('мана/энергия', 'прирост_мана/энергия'),
            'реген_маны/энергии': ('реген_маны/энергии', 'прирост_реген_маны/энергии'),
            'физ_атака': ('физ_атака', 'прирост_физ_атака'),
            'физ_защита': ('физ_защита', 'прирост_физ_защита'),
            'маг_защита': ('маг_защита', 'прирост_маг_защита'),
            'скорость_атаки': ('скорость_атаки', 'прирост_скорость_атаки')
        }
        
        if stat in growing_stats:
            base_stat, growth_stat = growing_stats[stat]
            query = f"""
            SELECT имя, 
                   {base_stat} + ({growth_stat} * (? - 1)) as calculated_stat
            FROM characters 
            ORDER BY calculated_stat DESC
            """
        else:
            query = f"""
            SELECT имя, {stat}
            FROM characters
            ORDER BY {stat} DESC
            """
        
        cursor.execute(query, (level,) if stat in growing_stats else ())
        results = cursor.fetchall()
        conn.close()
        
        return results
        
    except Exception as e:
        logger.error(f"Ошибка при получении данных из БД: {e}")
        return []

def register_handlers(bot):
    @bot.message_handler(commands=['chars_table'])
    def chars_table_cmd(message):
        try:
            kb = types.InlineKeyboardMarkup(row_width=2)
            for short_code, (btn_text, full_stat_name) in CHARACTERISTICS_MAP.items():
                kb.add(types.InlineKeyboardButton(
                    btn_text, 
                    callback_data=f"charTable::{short_code}"
                ))
            bot.send_message(
                message.chat.id,
                "Выберите характеристику для сравнения героев:",
                reply_markup=kb
            )
        except Exception as e:
            logger.error(f"Ошибка при отправке меню характеристик: {e}")
            bot.reply_to(message, "Произошла ошибка. Попробуйте позже.")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("charTable::"))
    def char_table_callback(call):
        try:
            short_code = call.data.split("::")[1]
            stat_name = CHARACTERISTICS_MAP[short_code][1]
            
            msg = bot.send_message(
                call.message.chat.id,
                "Введите уровень героя (1-15):"
            )
            bot.register_next_step_handler(msg, lambda m: process_level_input(m, bot, stat_name))
            
        except Exception as e:
            logger.error(f"Ошибка в обработке callback: {e}")
            bot.answer_callback_query(
                call.id,
                "Произошла ошибка. Попробуйте позже."
            )

def process_level_input(message, bot, stat_name):
    try:
        level = int(message.text.strip())
        if not 1 <= level <= 15:
            raise ValueError("Уровень должен быть от 1 до 15")
            
        results = get_heroes_by_stat(stat_name, level)
        
        if not results:
            bot.reply_to(message, "Не удалось получить данные героев.")
            return
            
        response = f"🏆 Рейтинг героев по '{stat_name}' на {level} уровне:\n\n"
        for idx, (hero, value) in enumerate(results[:10], 1):
            if value is not None:
                response += f"{idx}. {hero}: {round(float(value), 2)}\n"
            else:
                response += f"{idx}. {hero}: нет данных\n"
            
        bot.reply_to(message, response)
        
    except ValueError:
        bot.reply_to(
            message,
            "Пожалуйста, введите корректный уровень (от 1 до 15)."
        )
    except Exception as e:
        logger.error(f"Ошибка при обработке уровня: {e}")
        bot.reply_to(message, "Произошла ошибка. Попробуйте позже.")