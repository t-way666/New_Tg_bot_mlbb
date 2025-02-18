from telebot import types
import math

def calculate_damage_reduction(armor):
    """Рассчитывает снижение урона по значению защиты"""
    return (armor / (armor + 119)) * 100

def calculate_armor_needed(reduction):
    """Рассчитывает необходимую защиту для заданного снижения урона"""
    if reduction >= 100:
        return float('inf')
    return (119 * reduction) / (100 - reduction)

def armor_calculator(message, bot):
    """Основная функция калькулятора защиты"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("1 - Рассчитать необходимую защиту")
    btn2 = types.KeyboardButton("2 - Рассчитать снижение урона")
    markup.add(btn1, btn2)
    
    msg = bot.send_message(
        message.chat.id,
        "Что мы хотим рассчитать?\n\n"
        "1 - Сколько защиты нужно для желаемого снижения урона\n"
        "2 - Сколько снижения урона получим при заданной защите",
        reply_markup=markup
    )
    bot.register_next_step_handler(msg, process_choice, bot)

def process_choice(message, bot):
    """Обработка выбора пользователя"""
    if message.text.startswith("1"):
        msg = bot.send_message(
            message.chat.id,
            "Введите желаемый процент снижения урона (от 0 до 99.99):",
            reply_markup=types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(msg, calculate_armor, bot)
    elif message.text.startswith("2"):
        msg = bot.send_message(
            message.chat.id,
            "Введите количество защиты:",
            reply_markup=types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(msg, calculate_reduction, bot)
    else:
        bot.send_message(
            message.chat.id,
            "Пожалуйста, выберите 1 или 2",
            reply_markup=types.ReplyKeyboardRemove()
        )

def calculate_armor(message, bot):
    """Расчет необходимой защиты"""
    try:
        reduction = float(message.text)
        if reduction < 0 or reduction >= 100:
            raise ValueError("Процент должен быть от 0 до 99.99")
        
        armor = calculate_armor_needed(reduction)
        response = (
            f"Для получения {reduction:.2f}% снижения урона "
            f"необходимо {armor:.2f} защиты."
        )
        if reduction > 90:
            response += "\n\nОбратите внимание: такое количество защиты труднодостижимо в реальной игре!"
        
        bot.send_message(message.chat.id, response)
    except ValueError as e:
        bot.send_message(
            message.chat.id,
            f"Ошибка: {str(e)}\nПожалуйста, введите корректное число."
        )

def calculate_reduction(message, bot):
    """Расчет снижения урона"""
    try:
        armor = float(message.text)
        if armor < 0:
            raise ValueError("Защита не может быть отрицательной")
        
        reduction = calculate_damage_reduction(armor)
        response = (
            f"При {armor:.2f} защиты вы получите "
            f"{reduction:.2f}% снижения урона."
        )
        
        bot.send_message(message.chat.id, response)
    except ValueError as e:
        bot.send_message(
            message.chat.id,
            f"Ошибка: {str(e)}\nПожалуйста, введите корректное число."
        )