import time
from telebot import types
import math
from handlers.command_handler import handle_commands  # добавлен импорт

def calculate_damage_resistance(armor):
    """Рассчитывает снижение урона по значению защиты"""
    return (armor / (armor + 119)) * 100

def calculate_armor_needed(resistance):
    """Рассчитывает необходимую защиту для заданного снижения урона"""
    if resistance >= 100:
        return float('inf')
    return (119 * resistance) / (100 - resistance)

def armor_calculator(message, bot):
    """Функция-обработчик команды /armor_and_resistance"""
# Сначала удаляем старую клавиатуру
    bot.send_message(
        message.chat.id,
        "Подготовка калькулятора...",
        reply_markup=types.ReplyKeyboardRemove()
    )

    # Сначала удаляем старую клавиатуру
    bot.send_message(
        message.chat.id,
        "Подготовка калькулятора...",
        reply_markup=types.ReplyKeyboardRemove()
    )

    # Создаем разметку для inline-кнопок
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("1. Защита", callback_data="calc_armor")
    btn2 = types.InlineKeyboardButton("2. Снижение урона", callback_data="calc_resistance")
    markup.add(btn1, btn2)
    
    # Отправляем новое сообщение с inline-кнопками
    bot.send_message(
        message.chat.id,
        "Что мы хотим рассчитать?\n\n"
        "1 - Сколько защиты нужно для желаемого снижения урона\n"
        "2 - Сколько снижения урона получим при заданной защите",
        reply_markup=markup
    )

def register_handlers(bot):
    """Регистрация всех обработчиков для работы с защитой"""
    
    @bot.callback_query_handler(func=lambda call: call.data in ["calc_armor", "calc_resistance"])
    def handle_callback(call):
        if call.data == "calc_armor":
            msg = bot.send_message(
                call.message.chat.id,
                "Введите желаемый процент снижения урона (от 0 до 99.99):"
            )
            bot.register_next_step_handler(msg, lambda m: calculate_armor(m, bot))
        elif call.data == "calc_resistanse":
            msg = bot.send_message(
                call.message.chat.id,
                "Введите количество защиты:"
            )
            bot.register_next_step_handler(msg, lambda m: calculate_resistance(m, bot))
        bot.answer_callback_query(call.id)
        bot.delete_message(call.message.chat.id, call.message.message_id)

def calculate_armor(message, bot):
    """Расчет необходимой защиты"""
    try:
        resistance = float(message.text)
        if resistance < 0 or resistance >= 100:
            raise ValueError("Процент должен быть от 0 до 99.99")
        
        armor = (119 * resistance) / (100 - resistance)
        
        response = (
            f"Для получения {resistance:.2f}% снижения урона "
            f"необходимо {armor:.2f} защиты.\n\n"
            f"Формула расчета:\n"
            f"Y = (119 × X) ÷ (100 - X), где:\n"
            f"X - желаемый процент снижения урона\n"
            f"Y - необходимое количество защиты\n\n"
            f"Подставляем X = {resistance:.2f}:\n"
            f"Y = (119 × {resistance:.2f}) ÷ (100 - {resistance:.2f}) = {armor:.2f}"
        )
        if resistance > 90:
            response += "\n\nОбратите внимание: такое количество защиты труднодостижимо в реальной игре!"
        
        animate_text(bot, message.chat.id, response)
    except ValueError as e:
        animate_text(bot, message.chat.id, f"Ошибка: {str(e)}")

def calculate_resistance(message, bot):
    """Расчет снижения урона"""
    try:
        armor = float(message.text)
        if armor < 0:
            raise ValueError("Защита не может быть отрицательной")
        
        resistance = (armor / (armor + 119)) * 100
        
        response = (
            f"При {armor:.2f} защиты вы получите "
            f"{resistance:.2f}% снижения урона.\n\n"
            f"Формула расчета:\n"
            f"X = (Y ÷ (Y + 119)) × 100, где:\n"
            f"Y - количество защиты\n"
            f"X - процент снижения урона\n\n"
            f"Подставляем Y = {armor:.2f}:\n"
            f"X = ({armor:.2f} ÷ ({armor:.2f} + 119)) × 100 = {resistance:.2f}%"
        )
        
        animate_text(bot, message.chat.id, response)
    except ValueError as e:
        animate_text(bot, message.chat.id, f"Ошибка: {str(e)}")

def animate_text(bot, chat_id, text):
    """Анимация печати текста"""
    msg = bot.send_message(chat_id, "...")
    current_text = ""
    
    # Разбиваем текст на части
    chunks = []
    current_chunk = ""
    for word in text.split():
        if len(current_chunk) + len(word) + 1 <= 4096:  # Telegram limit
            current_chunk += (word + " ")
        else:
            chunks.append(current_chunk.strip())
            current_chunk = word + " "
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    # Анимируем текст по словам
    for chunk in chunks:
        try:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg.message_id,
                text=chunk,
                parse_mode='HTML'  # Добавляем поддержку HTML-форматирования
            )
            time.sleep(0.1)  # Увеличиваем задержку для более плавной анимации
        except Exception as e:
            if "message is not modified" not in str(e):
                print(f"Error: {e}")