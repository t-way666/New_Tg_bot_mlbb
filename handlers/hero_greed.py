from telebot.handler_backends import State, StatesGroup
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

def register_hero_greed_handlers(bot):  # Это имя должно совпадать с тем, что указано в command_mapping
    @bot.message_handler(commands=['hero_greed'])
    def hero_greed(message: Message):
        text = """
*Рейтинг жадности героев Mobile Legends*

💰 *Категории жадности:*
• *Высокая* - требуется 3+ полных предмета
• *Средняя* - требуется 2-3 предмета
• *Низкая* - достаточно 1-2 предмета
"""
        bot.send_message(message.chat.id, text, parse_mode="Markdown")
    return hero_greed  # Важно вернуть функцию-обработчик