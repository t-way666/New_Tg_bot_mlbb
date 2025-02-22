from telebot.handler_backends import State, StatesGroup
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

class SearchTeammatesStates(StatesGroup):
    waiting_for_rank = State()
    waiting_for_role = State()
    waiting_for_time = State()

def register_handlers(bot):
    @bot.message_handler(commands=['search_teammates'])
    def search_teammates(message: Message):
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("Создать анкету", callback_data="create_profile"),
            InlineKeyboardButton("Найти игроков", callback_data="find_players")
        )
        
        text = """
*🔍 Поиск тиммейтов*

Выберите действие:
• Создать анкету для поиска
• Найти игроков по параметрам

_В разработке: система рейтинга игроков, фильтры по времени игры и рангу_
"""
        bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
    return search_teammates