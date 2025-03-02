from telebot import types
import math
import logging

logger = logging.getLogger(__name__)

"""
ФОРМУЛЫ РАСЧЕТА УРОНА В MOBILE LEGENDS: BANG BANG

Общая формула расчета урона:
Итоговый урон = Общий урон атакующего × (120 / (120 + Эффективная защита))

Где:
1. Общий урон атакующего - это сумма всех источников урона:
   - Базовый урон героя
   - Бонусы от предметов
   - Множители от навыков
   - Бонусы от эмблем и талантов
   - Пассивные эффекты

2. Эффективная защита рассчитывается с учетом всех модификаторов:
   Эффективная защита = [
       (Базовая защита - Фиксированное снижение защиты) × 
       (1 - % снижения защиты)
   ] × (1 - % проникновения) - Фиксированное проникновение

3. Модификаторы защиты:
   - Фиксированное проникновение: уменьшает защиту на фиксированное значение
   - Процентное проникновение: уменьшает защиту на % от её значения
   - Фиксированное снижение защиты: уменьшает базовую защиту на фиксированное значение
   - Процентное снижение защиты: уменьшает защиту на % от её значения

Порядок применения модификаторов:
1. Сначала применяется снижение защиты (фиксированное, затем процентное)
2. Затем применяется проникновение (процентное, затем фиксированное)
"""

def calculate_damage(attacker_damage, target_defense, penetration_fixed=0, penetration_percent=0, defense_reduction_fixed=0, defense_reduction_percent=0):
    """
    Рассчитывает итоговый урон по формуле:
    Урон = Общий урон атакующего × (120 / (120 + Эффективная защита))
    
    Параметры:
    - attacker_damage: общий урон атакующего (с учетом всех бонусов)
    - target_defense: базовая защита цели
    - penetration_fixed: фиксированное проникновение (например, 15 от предмета Malefic Roar)
    - penetration_percent: процентное проникновение (например, 40% от предмета Divine Glaive)
    - defense_reduction_fixed: фиксированное снижение защиты (например, от способности Saber)
    - defense_reduction_percent: процентное снижение защиты (например, от способности Karina)
    
    Возвращает:
    - final_damage: итоговый урон
    - effective_defense: эффективная защита после всех модификаторов
    - damage_multiplier: множитель урона
    """
    # Расчет защиты после снижения
    defense_after_reduction = (target_defense - defense_reduction_fixed) * (1 - defense_reduction_percent / 100)
    
    # Расчет эффективной защиты с учетом проникновения
    effective_defense = defense_after_reduction * (1 - penetration_percent / 100) - penetration_fixed
    
    # Расчет итогового урона
    if effective_defense < 0:
        # Если эффективная защита отрицательная, урон увеличивается
        damage_multiplier = 120 / (120 + effective_defense)
    else:
        damage_multiplier = 120 / (120 + effective_defense)
    
    final_damage = attacker_damage * damage_multiplier
    
    return final_damage, effective_defense, damage_multiplier

def damage_calc(message, bot):
    """
    Функция-обработчик команды /damage_calculator
    
    Предлагает пользователю выбрать тип расчета:
    1. Простой расчет - учитывает только общий урон атакующего и защиту цели
    2. Продвинутый расчет - учитывает все модификаторы (проникновение, снижение защиты)
    """
    logger.info(f"Вызвана функция damage_calc для пользователя {message.from_user.id}")
    
    try:
        # Создаем инлайн-кнопки для выбора типа расчета
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn1 = types.InlineKeyboardButton(
            "Простой расчет", 
            callback_data="basic_damage"
        )
        btn2 = types.InlineKeyboardButton(
            "Продвинутый расчет", 
            callback_data="advanced_damage"
        )
        markup.add(btn1, btn2)
        
        # Отправляем сообщение с описанием и кнопками
        bot.send_message(
            message.chat.id,
            "Калькулятор урона в Mobile Legends: Bang Bang\n\n"
            "Выберите тип расчета:\n"
            "1. Простой расчет - учитывает только урон атакующего и защиту цели\n"
            "2. Продвинутый расчет - учитывает проникновение, снижение защиты и другие параметры",
            reply_markup=markup
        )
        logger.info(f"Отправлено сообщение с инлайн-кнопками пользователю {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"Ошибка при выполнении damage_calc: {e}")
        try:
            bot.send_message(message.chat.id, "Произошла ошибка при создании калькулятора урона. Пожалуйста, попробуйте позже.")
            logger.info("Отправлено сообщение об ошибке")
        except Exception as send_error:
            logger.error(f"Не удалось отправить сообщение об ошибке: {send_error}")

def register_handlers(bot):
    """Регистрация всех обработчиков для работы с калькулятором урона"""
    logger.info("Регистрация обработчиков для damage_calculator")
    
    # Обработчик для callback-запросов от инлайн-кнопок
    @bot.callback_query_handler(func=lambda call: call.data in ["basic_damage", "advanced_damage"])
    def handle_damage_calculator_callback(call):
        logger.info(f"Получен callback {call.data} от пользователя {call.from_user.id}")
        
        # Отвечаем на callback, чтобы убрать часы загрузки
        bot.answer_callback_query(call.id)
        
        if call.data == "basic_damage":
            # Запрашиваем урон атакующего
            msg = bot.send_message(
                call.message.chat.id,
                "Введите общий урон атакующего:\n"
                "(Это сумма базового урона героя и всех бонусов от предметов, эмблем и т.д.)"
            )
            bot.set_state(call.from_user.id, 'waiting_for_attacker_damage', call.message.chat.id)
            bot.register_next_step_handler(msg, lambda m: process_attacker_damage(m, bot))
            logger.info(f"Установлено состояние waiting_for_attacker_damage для пользователя {call.from_user.id}")
            
        elif call.data == "advanced_damage":
            # Запрашиваем урон атакующего для расширенного расчета
            msg = bot.send_message(
                call.message.chat.id,
                "Введите общий урон атакующего:\n"
                "(Это сумма базового урона героя и всех бонусов от предметов, эмблем и т.д.)"
            )
            bot.set_state(call.from_user.id, 'waiting_for_advanced_attacker_damage', call.message.chat.id)
            bot.register_next_step_handler(msg, lambda m: process_advanced_attacker_damage(m, bot))
            logger.info(f"Установлено состояние waiting_for_advanced_attacker_damage для пользователя {call.from_user.id}")
    
    # Добавляем обработчик для текстовых сообщений в состоянии ожидания ввода
    @bot.message_handler(func=lambda message: bot.get_state(message.from_user.id, message.chat.id) in [
        'waiting_for_attacker_damage', 'waiting_for_target_defense',
        'waiting_for_advanced_attacker_damage', 'waiting_for_advanced_target_defense',
        'waiting_for_penetration_fixed', 'waiting_for_penetration_percent',
        'waiting_for_defense_reduction_fixed', 'waiting_for_defense_reduction_percent'
    ])
    def handle_damage_calculator_input(message):
        logger.info(f"Получено сообщение в состоянии от пользователя {message.from_user.id}: {message.text}")
        current_state = bot.get_state(message.from_user.id, message.chat.id)
        
        # Проверяем, не является ли сообщение командой
        if message.text and message.text.startswith('/'):
            logger.info(f"Получена команда {message.text} вместо числа для калькулятора урона")
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
        
        # Обработка состояний для базового расчета
        if current_state == 'waiting_for_attacker_damage':
            process_attacker_damage(message, bot)
        elif current_state == 'waiting_for_target_defense':
            process_target_defense(message, bot)
        
        # Обработка состояний для расширенного расчета
        elif current_state == 'waiting_for_advanced_attacker_damage':
            process_advanced_attacker_damage(message, bot)
        elif current_state == 'waiting_for_advanced_target_defense':
            process_advanced_target_defense(message, bot)
        elif current_state == 'waiting_for_penetration_fixed':
            process_penetration_fixed(message, bot)
        elif current_state == 'waiting_for_penetration_percent':
            process_penetration_percent(message, bot)
        elif current_state == 'waiting_for_defense_reduction_fixed':
            process_defense_reduction_fixed(message, bot)
        elif current_state == 'waiting_for_defense_reduction_percent':
            process_defense_reduction_percent(message, bot)
    
    logger.info("Обработчики для damage_calculator успешно зарегистрированы")

def process_attacker_damage(message, bot):
    """Обработка ввода урона атакующего для базового расчета"""
    try:
        attacker_damage = float(message.text)
        if attacker_damage < 0:
            raise ValueError("Урон не может быть отрицательным")
        
        # Сохраняем введенное значение в данных пользователя
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['attacker_damage'] = attacker_damage
        
        # Запрашиваем защиту цели
        msg = bot.send_message(
            message.chat.id,
            "Введите защиту цели:\n"
            "(Это значение физической или магической защиты противника)"
        )
        bot.set_state(message.from_user.id, 'waiting_for_target_defense', message.chat.id)
        bot.register_next_step_handler(msg, lambda m: process_target_defense(m, bot))
        
    except ValueError as e:
        if "could not convert string to float" in str(e):
            bot.send_message(message.chat.id, "Ошибка: введите корректное число для урона")
        else:
            bot.send_message(message.chat.id, f"Ошибка: {str(e)}")
        
        # Повторно запрашиваем ввод
        msg = bot.send_message(message.chat.id, "Пожалуйста, введите общий урон атакующего:")
        bot.register_next_step_handler(msg, lambda m: process_attacker_damage(m, bot))

def process_target_defense(message, bot):
    """Обработка ввода защиты цели для базового расчета"""
    try:
        target_defense = float(message.text)
        if target_defense < 0:
            raise ValueError("Защита не может быть отрицательной")
        
        # Получаем сохраненное значение урона атакующего
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            attacker_damage = data['attacker_damage']
        
        # Рассчитываем урон
        final_damage, effective_defense, damage_multiplier = calculate_damage(
            attacker_damage=attacker_damage,
            target_defense=target_defense
        )
        
        # Рассчитываем процент снижения урона от защиты
        damage_reduction_percent = (target_defense / (target_defense + 120)) * 100
        
        # Рассчитываем, сколько урона было заблокировано защитой
        blocked_damage = attacker_damage - final_damage
        
        # Формируем ответ в более понятном виде
        response = (
            f"📊 Результаты расчета урона:\n\n"
            f"🔸 Общий урон атакующего: {attacker_damage:.0f}\n"
            f"🔹 Защита цели: {target_defense:.0f}\n\n"
            f"🛡️ Эффект защиты:\n"
            f"• Защита {target_defense:.0f} снижает урон на {damage_reduction_percent:.1f}%\n"
            f"• Заблокировано урона: {blocked_damage:.0f} ({(blocked_damage/attacker_damage*100):.1f}%)\n\n"
            f"💥 Итоговый урон: {final_damage:.0f} из {attacker_damage:.0f}\n\n"
            f"📝 Как это работает:\n"
            f"1. Процент снижения урона = Защита ÷ (Защита + 120) × 100%\n"
            f"2. {target_defense:.0f} ÷ ({target_defense:.0f} + 120) × 100% = {damage_reduction_percent:.1f}%\n"
            f"3. Итоговый урон = {attacker_damage:.0f} × (1 - {damage_reduction_percent:.1f}%) = {final_damage:.0f}"
        )
        
        bot.send_message(message.chat.id, response)
        
        # Сбрасываем состояние после успешного расчета
        bot.delete_state(message.from_user.id, message.chat.id)
        
    except ValueError as e:
        if "could not convert string to float" in str(e):
            bot.send_message(message.chat.id, "Ошибка: введите корректное число для защиты")
        else:
            bot.send_message(message.chat.id, f"Ошибка: {str(e)}")
        
        # Повторно запрашиваем ввод
        msg = bot.send_message(message.chat.id, "Пожалуйста, введите защиту цели:")
        bot.register_next_step_handler(msg, lambda m: process_target_defense(m, bot))

def process_advanced_attacker_damage(message, bot):
    """Обработка ввода урона атакующего для расширенного расчета"""
    try:
        attacker_damage = float(message.text)
        if attacker_damage < 0:
            raise ValueError("Урон не может быть отрицательным")
        
        # Сохраняем введенное значение в данных пользователя
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['attacker_damage'] = attacker_damage
        
        # Запрашиваем защиту цели
        msg = bot.send_message(
            message.chat.id,
            "Введите базовую защиту цели:\n"
            "(Это значение физической или магической защиты противника без учета снижений)"
        )
        bot.set_state(message.from_user.id, 'waiting_for_advanced_target_defense', message.chat.id)
        bot.register_next_step_handler(msg, lambda m: process_advanced_target_defense(m, bot))
        
    except ValueError as e:
        if "could not convert string to float" in str(e):
            bot.send_message(message.chat.id, "Ошибка: введите корректное число для урона")
        else:
            bot.send_message(message.chat.id, f"Ошибка: {str(e)}")
        
        # Повторно запрашиваем ввод
        msg = bot.send_message(message.chat.id, "Пожалуйста, введите общий урон атакующего:")
        bot.register_next_step_handler(msg, lambda m: process_advanced_attacker_damage(m, bot))

def process_advanced_target_defense(message, bot):
    """Обработка ввода защиты цели для расширенного расчета"""
    try:
        target_defense = float(message.text)
        if target_defense < 0:
            raise ValueError("Защита не может быть отрицательной")
        
        # Сохраняем введенное значение в данных пользователя
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['target_defense'] = target_defense
        
        # Запрашиваем фиксированное проникновение
        msg = bot.send_message(
            message.chat.id,
            "Введите фиксированное проникновение (0, если отсутствует):\n"
            "(Например, 15 от предмета Malefic Roar)"
        )
        bot.set_state(message.from_user.id, 'waiting_for_penetration_fixed', message.chat.id)
        bot.register_next_step_handler(msg, lambda m: process_penetration_fixed(m, bot))
        
    except ValueError as e:
        if "could not convert string to float" in str(e):
            bot.send_message(message.chat.id, "Ошибка: введите корректное число для защиты")
        else:
            bot.send_message(message.chat.id, f"Ошибка: {str(e)}")
        
        # Повторно запрашиваем ввод
        msg = bot.send_message(message.chat.id, "Пожалуйста, введите базовую защиту цели:")
        bot.register_next_step_handler(msg, lambda m: process_advanced_target_defense(m, bot))

def process_penetration_fixed(message, bot):
    """Обработка ввода фиксированного проникновения"""
    try:
        penetration_fixed = float(message.text)
        if penetration_fixed < 0:
            raise ValueError("Проникновение не может быть отрицательным")
        
        # Сохраняем введенное значение в данных пользователя
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['penetration_fixed'] = penetration_fixed
        
        # Запрашиваем процентное проникновение
        msg = bot.send_message(
            message.chat.id,
            "Введите процентное проникновение (0-100):\n"
            "(Например, 40% от предмета Divine Glaive)"
        )
        bot.set_state(message.from_user.id, 'waiting_for_penetration_percent', message.chat.id)
        bot.register_next_step_handler(msg, lambda m: process_penetration_percent(m, bot))
        
    except ValueError as e:
        if "could not convert string to float" in str(e):
            bot.send_message(message.chat.id, "Ошибка: введите корректное число для проникновения")
        else:
            bot.send_message(message.chat.id, f"Ошибка: {str(e)}")
        
        # Повторно запрашиваем ввод
        msg = bot.send_message(message.chat.id, "Пожалуйста, введите фиксированное проникновение (0, если отсутствует):")
        bot.register_next_step_handler(msg, lambda m: process_penetration_fixed(m, bot))

def process_penetration_percent(message, bot):
    """Обработка ввода процентного проникновения"""
    try:
        penetration_percent = float(message.text)
        if penetration_percent < 0 or penetration_percent > 100:
            raise ValueError("Процентное проникновение должно быть от 0 до 100")
        
        # Сохраняем введенное значение в данных пользователя
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['penetration_percent'] = penetration_percent
        
        # Запрашиваем фиксированное снижение защиты
        msg = bot.send_message(
            message.chat.id,
            "Введите фиксированное снижение защиты (0, если отсутствует):\n"
            "(Например, от способности Saber или других героев)"
        )
        bot.set_state(message.from_user.id, 'waiting_for_defense_reduction_fixed', message.chat.id)
        bot.register_next_step_handler(msg, lambda m: process_defense_reduction_fixed(m, bot))
        
    except ValueError as e:
        if "could not convert string to float" in str(e):
            bot.send_message(message.chat.id, "Ошибка: введите корректное число для процентного проникновения")
        else:
            bot.send_message(message.chat.id, f"Ошибка: {str(e)}")
        
        # Повторно запрашиваем ввод
        msg = bot.send_message(message.chat.id, "Пожалуйста, введите процентное проникновение (0-100):")
        bot.register_next_step_handler(msg, lambda m: process_penetration_percent(m, bot))

def process_defense_reduction_fixed(message, bot):
    """Обработка ввода фиксированного снижения защиты"""
    try:
        defense_reduction_fixed = float(message.text)
        if defense_reduction_fixed < 0:
            raise ValueError("Снижение защиты не может быть отрицательным")
        
        # Сохраняем введенное значение в данных пользователя
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['defense_reduction_fixed'] = defense_reduction_fixed
        
        # Запрашиваем процентное снижение защиты
        msg = bot.send_message(
            message.chat.id,
            "Введите процентное снижение защиты (0-100):\n"
            "(Например, от способности Karina или других героев)"
        )
        bot.set_state(message.from_user.id, 'waiting_for_defense_reduction_percent', message.chat.id)
        bot.register_next_step_handler(msg, lambda m: process_defense_reduction_percent(m, bot))
        
    except ValueError as e:
        if "could not convert string to float" in str(e):
            bot.send_message(message.chat.id, "Ошибка: введите корректное число для снижения защиты")
        else:
            bot.send_message(message.chat.id, f"Ошибка: {str(e)}")
        
        # Повторно запрашиваем ввод
        msg = bot.send_message(message.chat.id, "Пожалуйста, введите фиксированное снижение защиты (0, если отсутствует):")
        bot.register_next_step_handler(msg, lambda m: process_defense_reduction_fixed(m, bot))

def process_defense_reduction_percent(message, bot):
    """Обработка ввода процентного снижения защиты и расчет итогового урона"""
    try:
        defense_reduction_percent = float(message.text)
        if defense_reduction_percent < 0 or defense_reduction_percent > 100:
            raise ValueError("Процентное снижение защиты должно быть от 0 до 100")
        
        # Получаем все сохраненные значения
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            attacker_damage = data['attacker_damage']
            target_defense = data['target_defense']
            penetration_fixed = data['penetration_fixed']
            penetration_percent = data['penetration_percent']
            defense_reduction_fixed = data['defense_reduction_fixed']
        
        # Рассчитываем урон
        final_damage, effective_defense, damage_multiplier = calculate_damage(
            attacker_damage=attacker_damage,
            target_defense=target_defense,
            penetration_fixed=penetration_fixed,
            penetration_percent=penetration_percent,
            defense_reduction_fixed=defense_reduction_fixed,
            defense_reduction_percent=defense_reduction_percent
        )
        
        # Расчет промежуточных значений для подробного объяснения
        defense_after_reduction = (target_defense - defense_reduction_fixed) * (1 - defense_reduction_percent / 100)
        defense_after_penetration = defense_after_reduction * (1 - penetration_percent / 100) - penetration_fixed
        
        # Формируем ответ с подробным объяснением
        response = (
            f"Результаты расчета урона:\n\n"
            f"Общий урон атакующего: {attacker_damage:.2f}\n"
            f"Базовая защита цели: {target_defense:.2f}\n\n"
            f"Модификаторы защиты:\n"
            f"• Фиксированное снижение защиты: {defense_reduction_fixed:.2f}\n"
            f"• Процентное снижение защиты: {defense_reduction_percent:.2f}%\n"
            f"• Фиксированное проникновение: {penetration_fixed:.2f}\n"
            f"• Процентное проникновение: {penetration_percent:.2f}%\n\n"
            f"Защита после снижения: {defense_after_reduction:.2f}\n"
            f"Эффективная защита: {effective_defense:.2f}\n\n"
            f"Множитель урона: {damage_multiplier:.4f}\n"
            f"Итоговый урон: {final_damage:.2f}\n\n"
            f"Формула расчета:\n"
            f"1. Защита после снижения = ({target_defense:.2f} - {defense_reduction_fixed:.2f}) × (1 - {defense_reduction_percent:.2f}/100) = {defense_after_reduction:.2f}\n"
            f"2. Эффективная защита = {defense_after_reduction:.2f} × (1 - {penetration_percent:.2f}/100) - {penetration_fixed:.2f} = {effective_defense:.2f}\n"
            f"3. Урон = {attacker_damage:.2f} × (120 ÷ (120 + {effective_defense:.2f})) = {final_damage:.2f}"
        )
        
        bot.send_message(message.chat.id, response)
        
        # Сбрасываем состояние после успешного расчета
        bot.delete_state(message.from_user.id, message.chat.id)
        
    except ValueError as e:
        if "could not convert string to float" in str(e):
            bot.send_message(message.chat.id, "Ошибка: введите корректное число для процентного снижения защиты")
        else:
            bot.send_message(message.chat.id, f"Ошибка: {str(e)}")
        
        # Повторно запрашиваем ввод
        msg = bot.send_message(message.chat.id, "Пожалуйста, введите процентное снижение защиты (0-100):")
        bot.register_next_step_handler(msg, lambda m: process_defense_reduction_percent(m, bot)) 