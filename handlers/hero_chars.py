import sqlite3
import telebot
from telebot import types
import os
import random
import logging  # Добавляем импорт logging
from handlers.command_handler import handle_commands
from PIL import Image
import io
import tempfile

# Настраиваем логирование
logger = logging.getLogger(__name__)

# Путь к базе данных
DB_PATH = 'db/characters.db'

# Словарь для хранения последних показанных медиафайлов для каждого героя
last_shown_media = {}

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

def compress_image(image_path, max_size_mb=9):
    """Сжимает изображение до указанного размера в МБ"""
    try:
        # Открываем изображение
        img = Image.open(image_path)
        
        # Создаем временный файл для сжатого изображения
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            temp_path = temp_file.name
        
        # Начальное качество
        quality = 95
        
        # Сохраняем с максимальным качеством
        img.save(temp_path, format='JPEG', quality=quality, optimize=True)
        
        # Проверяем размер файла
        file_size = os.path.getsize(temp_path) / (1024 * 1024)  # в МБ
        
        # Если размер больше максимального, уменьшаем качество
        while file_size > max_size_mb and quality > 10:
            quality -= 5
            img.save(temp_path, format='JPEG', quality=quality, optimize=True)
            file_size = os.path.getsize(temp_path) / (1024 * 1024)
            logger.info(f"Сжимаем изображение: качество={quality}, размер={file_size:.2f} МБ")
        
        # Если размер все еще больше максимального, уменьшаем размер изображения
        if file_size > max_size_mb:
            # Определяем новый размер (уменьшаем на 10%)
            width, height = img.size
            new_width = int(width * 0.9)
            new_height = int(height * 0.9)
            
            while file_size > max_size_mb and new_width > 100 and new_height > 100:
                # Изменяем размер
                resized_img = img.resize((new_width, new_height), Image.LANCZOS)
                
                # Сохраняем с текущим качеством
                resized_img.save(temp_path, format='JPEG', quality=quality, optimize=True)
                
                # Проверяем размер
                file_size = os.path.getsize(temp_path) / (1024 * 1024)
                
                # Если все еще больше, уменьшаем еще на 10%
                if file_size > max_size_mb:
                    new_width = int(new_width * 0.9)
                    new_height = int(new_height * 0.9)
                    logger.info(f"Уменьшаем размер изображения: {new_width}x{new_height}, размер={file_size:.2f} МБ")
        
        logger.info(f"Изображение успешно сжато: {image_path} -> {temp_path}, размер={file_size:.2f} МБ")
        return temp_path
    except Exception as e:
        logger.error(f"Ошибка при сжатии изображения {image_path}: {e}")
        return None

def get_media_file(hero_name):
    """Получение случайного медиафайла героя, отличного от предыдущего"""
    media_dir = 'media/heroes'
    # Ищем все файлы героя по шаблону имя_героя_номер.расширение
    media_files = [f for f in os.listdir(media_dir) 
                   if f.lower().split('_')[0] == hero_name.lower() and 
                   f.lower().endswith(('.jpg', '.png', '.gif', '.mp4'))]
    
    if not media_files:
        return None, None
    
    # Если файлов меньше 2, то просто возвращаем случайный
    if len(media_files) < 2:
        selected_file = random.choice(media_files)
        media_path = os.path.join(media_dir, selected_file)
        media_type = os.path.splitext(selected_file)[1].lower()
        return process_media_file(media_path, media_type)
    
    # Получаем последний показанный файл для этого героя
    last_file = last_shown_media.get(hero_name.lower(), None)
    
    # Удаляем последний показанный файл из списка доступных
    available_files = [f for f in media_files if f != last_file]
    
    # Если все файлы были показаны (такого не должно быть, но на всякий случай)
    if not available_files:
        available_files = media_files
    
    # Перемешиваем список файлов для случайного выбора
    random.shuffle(available_files)
    
    # Пробуем найти подходящий файл
    for selected_file in available_files:
        media_path = os.path.join(media_dir, selected_file)
        media_type = os.path.splitext(selected_file)[1].lower()
        
        # Запоминаем этот файл как последний показанный
        last_shown_media[hero_name.lower()] = selected_file
        logger.info(f"Выбран медиафайл для героя {hero_name}: {selected_file}")
        
        return process_media_file(media_path, media_type)
    
    # Если не нашли подходящий файл, возвращаем None
    return None, None

def process_media_file(media_path, media_type):
    """Обрабатывает медиафайл в зависимости от его типа и размера"""
    try:
        # Проверяем размер файла
        file_size = os.path.getsize(media_path) / (1024 * 1024)  # в МБ
        
        # Для изображений
        if media_type in ['.jpg', '.png']:
            # Если размер больше лимита, отправляем как документ
            if file_size > 9:  # Оставляем запас в 1 МБ
                logger.info(f"Файл {media_path} слишком большой ({file_size:.2f} МБ), будет отправлен как документ")
                return media_path, 'document'
            return media_path, media_type
        
        # Для GIF и видео
        elif media_type in ['.gif', '.mp4']:
            # Если размер больше лимита, отправляем как документ
            if file_size > 49:  # Оставляем запас в 1 МБ
                logger.info(f"Файл {media_path} слишком большой ({file_size:.2f} МБ), будет отправлен как документ")
                return media_path, 'document'
            return media_path, media_type
        
        # Для неподдерживаемых типов
        else:
            logger.warning(f"Неподдерживаемый тип файла: {media_type}, будет отправлен как документ")
            return media_path, 'document'
            
    except Exception as e:
        logger.error(f"Ошибка при обработке медиафайла {media_path}: {e}")
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
                if media_type == 'document':
                    # Отправляем как документ
                    original_type = os.path.splitext(media_path)[1].lower()
                    file_name = f"{hero_name}{original_type}"
                    bot.send_document(
                        chat_id, 
                        media_file, 
                        caption=info, 
                        parse_mode="Markdown",
                        reply_markup=markup,
                        visible_file_name=file_name
                    )
                elif media_type == '.gif':
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
            
            # Удаляем временный файл, если это сжатое изображение
            if media_path.startswith(tempfile.gettempdir()):
                try:
                    os.remove(media_path)
                    logger.info(f"Удален временный файл: {media_path}")
                except Exception as e:
                    logger.error(f"Ошибка при удалении временного файла {media_path}: {e}")
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
            logger.info(f"Обработка уровня героя: {hero_name}, сообщение: {message.text}, chat_id: {message.chat.id}")
            
            # Если получена новая команда
            if message.text.startswith('/'):
                # Очищаем состояние пользователя
                if message.chat.id in user_states:
                    del user_states[message.chat.id]
                # Отменяем регистрацию следующего шага
                bot.clear_step_handler_by_chat_id(message.chat.id)
                # Убираем клавиатуру
                markup = types.ReplyKeyboardRemove()
                bot.send_message(message.chat.id, "Переключение на новую команду...", reply_markup=markup)
                # Передаем управление обработчику команд
                handle_commands(bot, message)
                return

            # Остальная логика обработки уровня героя
            if message.chat.id not in user_states or user_states[message.chat.id] != 'choosing_level':
                logger.warning(f"Неверное состояние пользователя: {user_states.get(message.chat.id, 'отсутствует')}")
                # Устанавливаем состояние выбора уровня
                user_states[message.chat.id] = 'choosing_level'

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
            
            # Отправляем информацию о герое
            logger.info(f"Отправка информации о герое {hero_name} с уровнем {level}")
            send_hero_info(bot, message.chat.id, hero_name, level)
            
            # Убираем клавиатуру после отправки информации
            markup = types.ReplyKeyboardRemove()
            bot.send_message(message.chat.id, "Информация о герое обновлена", reply_markup=markup)
            
        except ValueError as e:
            logger.error(f"Ошибка при обработке уровня героя: {e}")
            markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True, one_time_keyboard=True)
            markup.row('1', '4', '8', '12', '15')
            msg = bot.send_message(
                message.chat.id, 
                "Пожалуйста, введите число от 1 до 15:", 
                reply_markup=markup
            )
            bot.register_next_step_handler(msg, process_hero_level, hero_name)
        except Exception as e:
            logger.error(f"Непредвиденная ошибка при обработке уровня героя: {e}")
            bot.send_message(message.chat.id, "Произошла ошибка. Пожалуйста, попробуйте снова.")

    # Перемещаем обработчик кнопки "Выбрать другого героя" внутрь функции register_hero_handlers
    @bot.callback_query_handler(func=lambda call: call.data == "select_new_hero")
    def select_new_hero(call):
        send_role_selection(call.message)
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("change_level::"))
    def change_hero_level(call):
        hero_name = call.data.split("::")[1]
        user_states[call.message.chat.id] = 'choosing_level'
        logger.info(f"Изменение уровня героя {hero_name}, chat_id: {call.message.chat.id}")
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