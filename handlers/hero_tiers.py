from telebot.handler_backends import State, StatesGroup
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

class HeroTiersStates(StatesGroup):
    waiting_for_tier_type = State()  # Выбор типа тир-листа

def register_hero_tiers_handlers(bot):  # Это имя должно совпадать с тем, что указано в command_mapping
    @bot.message_handler(commands=['hero_tiers'])
    def hero_tiers(message: Message):
        text = """
*Тир-листы героев Mobile Legends*

Выберите тип тир-листа:
• Соло
• Дуо
• Трио
• 5-stack (фулл пати)
• По позициям
"""
        bot.send_message(message.chat.id, text, parse_mode="Markdown")
    return hero_tiers  # Важно вернуть функцию-обработчик