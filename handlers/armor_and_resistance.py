from telebot import types
import math
import logging

logger = logging.getLogger(__name__)

def calculate_damage_resistance(armor):
    """Рассчитывает снижение урона по значению защиты"""
    return (armor / (armor + 120)) * 100

def calculate_armor_needed(resistance):
    """Рассчитывает необходимую защиту для заданного снижения урона"""
    if resistance >= 100:
        return float('inf')
    return (120 * resistance) / (100 - resistance)

def armor_calculator(message, bot):
    """Функция-обработчик команды /armor_and_resistance"""
    logger.info(f"Вызвана функция armor_calculator для пользователя {message.from_user.id}")
    
    try:
        # Создаем инлайн-кнопки с цифрами
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton(
            "1", 
            callback_data="calc_armor"
        )
        btn2 = types.InlineKeyboardButton(
            "2", 
            callback_data="calc_resistance"
        )
        markup.add(btn1, btn2)
        
        # Отправляем сообщение с вопросами и инлайн-кнопками
        bot.send_message(
            message.chat.id,
            "Что мы хотим рассчитать?\n\n"
            "1. Сколько защиты нужно для желаемого снижения урона\n"
            "2. Сколько снижения урона получим при заданной защите",
            reply_markup=markup
        )
        logger.info(f"Отправлено сообщение с инлайн-кнопками пользователю {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"Ошибка при выполнении armor_calculator: {e}")
        try:
            bot.send_message(message.chat.id, "Произошла ошибка при создании калькулятора. Пожалуйста, попробуйте позже.")
            logger.info("Отправлено сообщение об ошибке")
        except Exception as send_error:
            logger.error(f"Не удалось отправить сообщение об ошибке: {send_error}")

def register_handlers(bot):
    """Регистрация всех обработчиков для работы с защитой"""
    logger.info("Регистрация обработчиков для armor_and_resistance")
    
    # Обработчик для команды /armor_and_resistance регистрируется в Run.py
    # Здесь регистрируем только обработчики состояний и callback-запросов
    
    # Обработчик для callback-запросов от инлайн-кнопок
    @bot.callback_query_handler(func=lambda call: call.data in ["calc_armor", "calc_resistance"])
    def handle_armor_resistance_callback(call):
        logger.info(f"Получен callback {call.data} от пользователя {call.from_user.id}")
        
        # Отвечаем на callback, чтобы убрать часы загрузки
        bot.answer_callback_query(call.id)
        
        if call.data == "calc_armor":
            msg = bot.send_message(
                call.message.chat.id,
                "Введите желаемый процент снижения урона (от 0 до 99.99):"
            )
            bot.set_state(call.from_user.id, 'waiting_for_resistance', call.message.chat.id)
            bot.register_next_step_handler(msg, lambda m: calculate_armor(m, bot))
            logger.info(f"Установлено состояние waiting_for_resistance для пользователя {call.from_user.id}")
            
        elif call.data == "calc_resistance":
            msg = bot.send_message(
                call.message.chat.id,
                "Введите количество защиты:"
            )
            bot.set_state(call.from_user.id, 'waiting_for_armor', call.message.chat.id)
            bot.register_next_step_handler(msg, lambda m: calculate_resistance(m, bot))
            logger.info(f"Установлено состояние waiting_for_armor для пользователя {call.from_user.id}")
    
    # Добавляем обработчик для текстовых сообщений в состоянии ожидания ввода
    @bot.message_handler(func=lambda message: bot.get_state(message.from_user.id, message.chat.id) in ['waiting_for_armor', 'waiting_for_resistance'])
    def handle_armor_resistance_input(message):
        logger.info(f"Получено сообщение в состоянии от пользователя {message.from_user.id}: {message.text}")
        current_state = bot.get_state(message.from_user.id, message.chat.id)
        
        if current_state == 'waiting_for_resistance':
            calculate_armor(message, bot)
        elif current_state == 'waiting_for_armor':
            calculate_resistance(message, bot)
    
    logger.info("Обработчики для armor_and_resistance успешно зарегистрированы")

def calculate_armor(message, bot):
    """Расчет необходимой защиты"""
    try:
        # Проверяем, не является ли сообщение командой
        if message.text and message.text.startswith('/'):
            logger.info(f"Получена команда {message.text} вместо числа для расчета защиты")
            # Сбрасываем состояние и позволяем обработчику команд обработать сообщение
            bot.delete_state(message.from_user.id, message.chat.id)
            
            # Перенаправляем сообщение на обработчик команд
            from Run import command_handlers
            command = message.text.split()[0].lower()
            if command in command_handlers:
                logger.info(f"Перенаправление на обработчик команды {command}")
                command_handlers[command](message)
            else:
                bot.send_message(message.chat.id, f"Неизвестная команда: {command}. Используйте /help для списка команд.")
            return
            
        resistance = float(message.text)
        if resistance < 0 or resistance >= 100:
            raise ValueError("Процент должен быть от 0 до 99.99")
        
        armor = (120 * resistance) / (100 - resistance)
        
        response = (
            f"Для получения {resistance:.2f}% снижения урона "
            f"необходимо {armor:.2f} защиты.\n\n"
            f"Формула расчета:\n"
            f"Y = (120 × X) ÷ (100 - X), где:\n"
            f"X - желаемый процент снижения урона\n"
            f"Y - необходимое количество защиты\n\n"
            f"Подставляем X = {resistance:.2f}:\n"
            f"Y = (120 × {resistance:.2f}) ÷ (100 - {resistance:.2f}) = {armor:.2f}"
        )
        if resistance > 90:
            response += "\n\nОбратите внимание: такое количество защиты труднодостижимо в реальной игре!"
        
        bot.send_message(message.chat.id, response, parse_mode='HTML')
        # Сбрасываем состояние после успешного расчета
        bot.delete_state(message.from_user.id, message.chat.id)
    except ValueError as e:
        if "could not convert string to float" in str(e):
            bot.send_message(message.chat.id, f"Ошибка: введите корректное число для расчета")
        else:
            bot.send_message(message.chat.id, f"Ошибка: {str(e)}")
        # Повторно запрашиваем ввод
        msg = bot.send_message(message.chat.id, "Пожалуйста, введите желаемый процент снижения урона (от 0 до 99.99):")
        bot.register_next_step_handler(msg, lambda m: calculate_armor(m, bot))

def calculate_resistance(message, bot):
    """Расчет снижения урона"""
    try:
        # Проверяем, не является ли сообщение командой
        if message.text and message.text.startswith('/'):
            logger.info(f"Получена команда {message.text} вместо числа для расчета снижения урона")
            # Сбрасываем состояние и позволяем обработчику команд обработать сообщение
            bot.delete_state(message.from_user.id, message.chat.id)
            
            # Перенаправляем сообщение на обработчик команд
            from Run import command_handlers
            command = message.text.split()[0].lower()
            if command in command_handlers:
                logger.info(f"Перенаправление на обработчик команды {command}")
                command_handlers[command](message)
            else:
                bot.send_message(message.chat.id, f"Неизвестная команда: {command}. Используйте /menu для списка команд.")
            return
            
        armor = float(message.text)
        if armor < 0:
            raise ValueError("Защита не может быть отрицательной")
        
        resistance = (armor / (armor + 120)) * 100
        
        response = (
            f"При {armor:.2f} защиты вы получите "
            f"{resistance:.2f}% снижения урона.\n\n\n"
            f"Формула расчета:\n"
            f"X = (Y ÷ (Y + 120)) × 100, где:\n"
            f"Y - количество защиты\n"
            f"X - процент снижения урона\n\n"
            f"Подставляем Y = {armor:.2f}:\n"
            f"X = ({armor:.2f} ÷ ({armor:.2f} + 120)) × 100 = {resistance:.2f}%"
        )
        
        bot.send_message(message.chat.id, response, parse_mode='HTML')
        # Сбрасываем состояние после успешного расчета
        bot.delete_state(message.from_user.id, message.chat.id)
    except ValueError as e:
        if "could not convert string to float" in str(e):
            bot.send_message(message.chat.id, f"Ошибка: введите корректное число для расчета")
        else:
            bot.send_message(message.chat.id, f"Ошибка: {str(e)}")
        # Повторно запрашиваем ввод
        msg = bot.send_message(message.chat.id, "Пожалуйста, введите количество защиты:")
        bot.register_next_step_handler(msg, lambda m: calculate_resistance(m, bot))