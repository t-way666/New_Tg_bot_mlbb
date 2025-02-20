import sqlite3
import telebot
from telebot import types
import os
import random
import logging  # Добавляем импорт logging

# Настраиваем логирование
logger = logging.getLogger(__name__)

# Путь к базе данных
DB_PATH = 'db/characters.db'

# Функция для получения информации о герое из базы данных
def get_character_info(name, level=15):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Получение основной информации о герое
    cursor.execute("SELECT * FROM hero_names WHERE имя=?", (name,))
    hero = cursor.fetchone()
    if not hero:
        return f"Герой {name} не найден."

    hero_id = hero[0]
    hero_name = hero[1].capitalize()

    # Получение ролей героя
    cursor.execute("SELECT * FROM hero_role WHERE character_id=?", (hero_id,))
    roles = cursor.fetchone()
    role_str = "-".join([role for role, value in zip(['убийца', 'стрелок', 'маг', 'танк', 'боец', 'поддержка'], roles[1:]) if value])
    role_str = role_str if role_str else "не указано"

    # Получение характеристик героя
    cursor.execute("SELECT * FROM hero_chars_no_up WHERE character_id=?", (hero_id,))
    chars_no_up = cursor.fetchone()

    cursor.execute("SELECT * FROM hero_chars_up WHERE character_id=?", (hero_id,))
    chars_up = cursor.fetchone()

    conn.close()

    # Формирование ответа
    resp = f"✨ **Информация о {hero_name} (ур. {level})** ✨\n\n"
    resp += f"**Роль:** {role_str}\n\n"

    # Характеристики с приростом
    growth_fields = {
        'ОЗ': 1, 'реген ОЗ': 2, 'мана/энергия': 3, 'реген маны/энергии': 4,
        'физ атака': 5, 'физ защита': 6, 'маг защита': 7, 'скорость атаки': 8
    }
    resp += "**Характеристики (с приростом):**\n"
    for label, idx in growth_fields.items():
        base_val = chars_no_up[idx]
        growth_rate = chars_up[idx]
        final_val = round(base_val + growth_rate * (level - 1), 2)
        resp += f"• {label}: {final_val}\n"

    # Статичные характеристики
    static_fields = {
        'маг сила': 9, 'коэффициент скорости атаки %': 10, 'скорость передвижения': 11,
        'мин. дальность базовой атаки': 12, 'макс. дальность базовой атаки': 13,
        'шанс крита': 14, 'крит урон': 15, 'сокращение перезарядки': 16,
        'физ проникновение': 17, 'маг проникновение': 18, 'вампиризм': 19,
        'вампиризм навыков': 20, 'устойчивость': 21, 'уменьшение крит урона': 22,
        'эффект лечения': 23, 'полученное лечение': 24
    }
    resp += "\n**Статичные характеристики:**\n"
    for label, idx in static_fields.items():
        resp += f"• {label}: {chars_no_up[idx]}\n"

    return resp

def get_media_file(hero_name):
    """Получение случайного медиафайла героя"""
    media_dir = 'media/heroes'
    # Ищем все файлы героя по шаблону имя_героя_номер.расширение
    media_files = [f for f in os.listdir(media_dir) 
                   if f.lower().split('_')[0] == hero_name.lower() and 
                   f.lower().endswith(('.jpg', '.png', '.gif', '.mp4'))]
    
    if not media_files:
        return None, None

    # Перемешиваем список файлов для случайного выбора
    random.shuffle(media_files)
    
    # Пробуем найти подходящий файл
    for selected_file in media_files:
        media_path = os.path.join(media_dir, selected_file)
        media_type = os.path.splitext(selected_file)[1].lower()
        
        # Проверяем размер файла (ограничение 10MB для фото и 50MB для видео/gif)
        file_size = os.path.getsize(media_path)
        if (media_type in ['.jpg', '.png'] and file_size <= 10 * 1024 * 1024) or \
           (media_type in ['.gif', '.mp4'] and file_size <= 50 * 1024 * 1024):
            return media_path, media_type
        else:
            logger.warning(f"Файл {selected_file} слишком большой, пробуем следующий")
    
    return None, None

def send_hero_info(bot, chat_id, hero_name, level):
    """Отправка информации о герое вместе с медиафайлом"""
    info = get_character_info(hero_name, level)
    
    try:
        # Добавляем кнопки действий
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn_new_level = types.InlineKeyboardButton(
            "Изменить уровень", 
            callback_data=f"change_level::{hero_name}"
        )
        btn_new_hero = types.InlineKeyboardButton(
            "Выбрать другого героя", 
            callback_data="select_new_hero"
        )
        markup.add(btn_new_level, btn_new_hero)

        # Используем локальные файлы
        media_path, media_type = get_media_file(hero_name)
        if media_path:
            with open(media_path, 'rb') as media_file:
                if media_type == '.gif':
                    bot.send_animation(
                        chat_id, 
                        media_file, 
                        caption=info, 
                        parse_mode="Markdown",
                        reply_markup=markup
                    )
                elif media_type in ['.jpg', '.png']:
                    bot.send_photo(
                        chat_id, 
                        media_file, 
                        caption=info, 
                        parse_mode="Markdown",
                        reply_markup=markup
                    )
                elif media_type == '.mp4':
                    bot.send_video(
                        chat_id, 
                        media_file, 
                        caption=info, 
                        parse_mode="Markdown",
                        reply_markup=markup
                    )
        else:
            bot.send_message(
                chat_id, 
                info, 
                parse_mode="Markdown",
                reply_markup=markup
            )
            
    except Exception as e:
        logger.error(f"Ошибка при отправке медиафайла: {e}")
        bot.send_message(
            chat_id, 
            info, 
            parse_mode="Markdown",
            reply_markup=markup
        )

# Регистрация обработчиков команд
def register_hero_handlers(bot: telebot.TeleBot):
    # Добавляем словарь для отслеживания состояния пользователей
    user_states = {}
    
    @bot.message_handler(commands=['hero_chars'])
    def hero_command_handler(message):
        user_states[message.chat.id] = 'choosing_role'
        send_role_selection(message)

    def send_role_selection(message):
        markup = types.InlineKeyboardMarkup(row_width=3)
        roles = ['убийца', 'стрелок', 'маг', 'танк', 'боец', 'поддержка']
        for role in roles:
            btn = types.InlineKeyboardButton(role.capitalize(), callback_data=f"heroRole::{role}")
            markup.add(btn)
        bot.send_message(message.chat.id, "Выберите роль героя:", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("heroRole::"))
    def hero_role_handler(call):
        role = call.data.split("::")[1]
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"SELECT hero_names.имя FROM hero_names JOIN hero_role ON hero_names.id = hero_role.character_id WHERE hero_role.{role} = 1")
        matching_heroes = cursor.fetchall()
        conn.close()
        
        if not matching_heroes:
            bot.send_message(call.message.chat.id, f"Героев с ролью '{role}' не найдено.")
            return
            
        markup = types.InlineKeyboardMarkup(row_width=2)
        for hero in sorted(matching_heroes):
            btn = types.InlineKeyboardButton(hero[0].capitalize(), callback_data=f"heroName::{hero[0]}")
            markup.add(btn)
        bot.send_message(call.message.chat.id, f"Герои с ролью '{role}':", reply_markup=markup)
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("heroName::"))
    def hero_by_role_selected(call):
        hero_name = call.data.split("::")[1]
        user_states[call.message.chat.id] = 'choosing_level'
        markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True, one_time_keyboard=True)
        # Добавляем кнопки с уровнями 1, 4, 8, 12, 15 для быстрого выбора
        markup.row('1', '4', '8', '12', '15')
        msg = bot.send_message(
            call.message.chat.id, 
            f"Вы выбрали героя: {hero_name.capitalize()}\nВыберите или введите уровень героя (1-15):", 
            reply_markup=markup
        )
        bot.register_next_step_handler(msg, process_hero_level, hero_name)
        bot.answer_callback_query(call.id)

    def process_hero_level(message, hero_name):
        try:
            # Проверяем состояние пользователя
            if message.chat.id not in user_states or user_states[message.chat.id] != 'choosing_level':
                return

            level = int(message.text.strip())
            if level < 1 or level > 15:
                markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True, one_time_keyboard=True)
                markup.row('1', '4', '8', '12', '15')
                msg = bot.send_message(
                    message.chat.id, 
                    "Уровень должен быть числом от 1 до 15. Выберите или введите уровень снова:", 
                    reply_markup=markup
                )
                bot.register_next_step_handler(msg, process_hero_level, hero_name)
                return
            
            # Отправляем информацию о герое напрямую
            send_hero_info(bot, message.chat.id, hero_name, level)
            
        except ValueError:
            markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True, one_time_keyboard=True)
            markup.row('1', '4', '8', '12', '15')
            msg = bot.send_message(
                message.chat.id, 
                "Пожалуйста, введите число от 1 до 15:", 
                reply_markup=markup
            )
            bot.register_next_step_handler(msg, process_hero_level, hero_name)

    # Перемещаем обработчик кнопки "Выбрать другого героя" внутрь функции register_hero_handlers
    @bot.callback_query_handler(func=lambda call: call.data == "select_new_hero")
    def select_new_hero(call):
        send_role_selection(call.message)
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("change_level::"))
    def change_hero_level(call):
        hero_name = call.data.split("::")[1]
        markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True, one_time_keyboard=True)
        markup.row('1', '4', '8', '12', '15')
        msg = bot.send_message(
            call.message.chat.id, 
            f"Выберите новый уровень для героя {hero_name.capitalize()} (1-15):", 
            reply_markup=markup
        )
        bot.register_next_step_handler(msg, process_hero_level, hero_name)
        bot.answer_callback_query(call.id)

    return hero_command_handler

# Если файл запускается напрямую (например, для тестирования)
if __name__ == "__main__":
    from config.settings import API_TOKEN
    bot = telebot.TeleBot(API_TOKEN)
    register_hero_handlers(bot)
    print("Бот запущен, команда /hero_chars активна.")
    bot.infinity_polling()