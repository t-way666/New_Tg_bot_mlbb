import time
import os
import random
import logging
from telebot import types

# Настраиваем логирование
logger = logging.getLogger(__name__)

def get_random_media():
    """Получает случайный медиафайл из папки start_gifs"""
    media_dir = 'media/start_gifs'  # Изменен путь к папке
    try:
        if not os.path.exists(media_dir):
            logger.error(f"Папка {media_dir} не существует")
            return None
            
        media_files = [f for f in os.listdir(media_dir) 
                      if f.lower().endswith(('.gif', '.jpg', '.png', '.mp4'))]
        
        if not media_files:
            logger.warning(f"В папке {media_dir} нет подходящих медиафайлов")
            return None
            
        selected_file = random.choice(media_files)
        logger.info(f"Выбран файл: {selected_file}")
        return os.path.join(media_dir, selected_file)
        
    except Exception as e:
        logger.error(f"Ошибка при получении медиафайла: {e}")
        return None

def send_media(bot, chat_id, media_path):
    """Отправка медиафайла в зависимости от его типа"""
    try:
        if not os.path.exists(media_path):
            logger.error(f"Файл не найден: {media_path}")
            return False

        with open(media_path, 'rb') as media_file:
            if media_path.lower().endswith('.gif'):
                bot.send_animation(chat_id, media_file)
            elif media_path.lower().endswith(('.jpg', '.png')):
                bot.send_photo(chat_id, media_file)
            elif media_path.lower().endswith('.mp4'):
                bot.send_video(chat_id, media_file, timeout=60)
        return True
        
    except Exception as e:
        logger.error(f"Ошибка при отправке медиафайла: {e}")
        return False

def send_start(bot):
    @bot.message_handler(commands=['start'])
    def send_start_message(message):
        try:
            user_first_name = message.from_user.first_name

            # Создаем клавиатуру с основными командами
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.row('/help', '/rank', '/my_stars')
            markup.row('/winrate_correction', '/season_progress')
            markup.row('/armor_and_resistance')

            # Приветственное сообщение
            greeting = (
                f"👋 Привет, {user_first_name}!\n\n"
                "Я помогу тебе с расчетами в Mobile Legends. \n"
                "Вот доступные команды:\n\n"
                
                " /start - старт/рестартбота \n"
                " /rank - Определить ранг по звездам\n"
                " /my_stars - Подсчет общего количества звезд\n"
                " /winrate_correction - Корректировка винрейта\n"
                " /season_progress - Сколько игр нужно сыграть для достижения желаемого ранга\n"
                " /armor_and_resistance - Калькулятор защиты и снижения урона\n\n"
                
                " Команды которые в разработке(пока не работают):\n"
                " /help - Помощь\n"
                " /support\n"
                " /guide\n"
                " /cybersport_info\n"
                " /chars_table\n"
                " /hero_chars\n"
                " /hero_greed\n"
                " /hero_tiers\n"
                " /search_teammates\n"
                " /img_creator\n"
            )

            bot.send_message(
                message.chat.id,
                greeting,
                reply_markup=markup,
                parse_mode='HTML'
            )

        except Exception as e:
            logger.error(f"Ошибка в команде start: {e}")
            bot.reply_to(message, "Произошла ошибка при запуске бота. Попробуйте позже.")

    return send_start_message