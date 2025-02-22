from telebot.handler_backends import State, StatesGroup
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

def register_handlers(bot):
    @bot.message_handler(commands=['img_creator'])
    def img_creator(message: Message):
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("Аватарка", callback_data="create_avatar"),
            InlineKeyboardButton("Баннер", callback_data="create_banner")
        )
        
        text = """
*🎨 Создание изображений*

Выберите тип изображения:
• Аватарка для профиля
• Баннер для профиля

_В разработке: генерация изображений, шаблоны, настройка стилей_
"""
        bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
    return img_creator