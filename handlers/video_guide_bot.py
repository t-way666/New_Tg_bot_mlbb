from telebot.handler_backends import State, StatesGroup
from telebot.types import Message

def register_handlers(bot):
    @bot.message_handler(commands=['video_guide'])
    def video_guide(message: Message):
        text = """
*📹 Видео-гайд по использованию бота*

🎥 *Доступные видео:*
• Основные команды бота
• Калькуляторы и расчеты
• Работа с героями
• Поиск тиммейтов
• Дополнительные функции

_В разработке: создание видео-контента_
"""
        bot.send_message(message.chat.id, text, parse_mode="Markdown")
    return video_guide