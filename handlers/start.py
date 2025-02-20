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

            # Приветственное сообщение
            greeting = (
                f"👋 Привет, {user_first_name}!\n\n"
                "Я бот помощник по Mobile Legends. \n"
                "Используй команду /menu чтобы увидеть список доступных команд."
            )

            bot.send_message(
                message.chat.id,
                greeting,
                parse_mode='HTML'
            )

        except Exception as e:
            logger.error(f"Ошибка в команде start: {e}")
            bot.reply_to(message, "Произошла ошибка при запуске бота. Попробуйте позже.")

    return send_start_message