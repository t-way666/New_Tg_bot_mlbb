from telebot.handler_backends import State, StatesGroup
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import logging

logger = logging.getLogger(__name__)

def register_handlers(bot):
    @bot.message_handler(commands=['support'])
    def support(message: Message):
        try:
            markup = InlineKeyboardMarkup()
            markup.row(
                InlineKeyboardButton("Оставить отзыв", callback_data="leave_feedback"),
                InlineKeyboardButton("Сообщить об ошибке", callback_data="report_bug")
            )
            markup.row(
                InlineKeyboardButton("Разработчик", url="https://t.me/T_w_a_y")
            )
            
            text = (
                "🛠 *Поддержка*\n\n"
                "• Оставить отзыв о работе бота\n"
                "• Сообщить об ошибке\n"
                "• Связаться с разработчиком\n\n"
                "*Разработчик:* [@T\_w\_a\_y](https://t.me/T_w_a_y)\n\n"
                "_Спасибо за использование бота\!_"
            )
            
            bot.send_message(
                message.chat.id, 
                text, 
                reply_markup=markup, 
                parse_mode="MarkdownV2",
                disable_web_page_preview=True
            )
        except Exception as e:
            logger.error(f"Ошибка в обработчике support: {e}")
            bot.reply_to(message, "Произошла ошибка. Попробуйте позже.")
            
    return support