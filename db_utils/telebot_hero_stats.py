from hero_calculator import calculate_hero_stats
import sqlite3
import json
import telebot
from telebot import types

def get_heroes_list():
    """
    Получает список всех героев из базы данных.
    
    Returns:
        list: Список имен героев
    """
    try:
        conn = sqlite3.connect('../db/characters.db')
        cursor = conn.cursor()
        cursor.execute("SELECT имя FROM hero_names ORDER BY имя")
        heroes = [row[0] for row in cursor.fetchall()]
        conn.close()
        return heroes
    except sqlite3.Error as e:
        print(f"Ошибка SQLite: {e}")
        return []

def get_heroes_by_role():
    """
    Получает список героев, сгруппированных по ролям.
    
    Returns:
        dict: Словарь {роль: [список героев]}
    """
    try:
        conn = sqlite3.connect('../db/characters.db')
        cursor = conn.cursor()
        cursor.execute("""
        SELECT h.имя, r.роль 
        FROM hero_names h
        JOIN hero_roles r ON h.id = r.character_id
        ORDER BY r.роль, h.имя
        """)
        
        heroes_by_role = {}
        for hero_name, role in cursor.fetchall():
            if role not in heroes_by_role:
                heroes_by_role[role] = []
            heroes_by_role[role].append(hero_name)
        
        conn.close()
        return heroes_by_role
    except sqlite3.Error as e:
        print(f"Ошибка SQLite: {e}")
        return {}

def format_hero_stats(stats):
    """
    Форматирует характеристики героя для вывода в Telegram.
    
    Args:
        stats (dict): Словарь с характеристиками героя
    
    Returns:
        str: Отформатированная строка с характеристиками
    """
    if not stats:
        return "Не удалось получить характеристики героя."
    
    result = f"Характеристики героя {stats['имя']} на уровне {stats['уровень']}:\n\n"
    
    # Группировка характеристик по категориям
    categories = {
        'Здоровье и мана': ['ОЗ', 'реген_ОЗ', 'мана/энергия', 'реген_маны/энергии'],
        'Атака и защита': ['физ_атака', 'физ_защита', 'маг_защита', 'маг_сила'],
        'Скорость': ['скорость_атаки', 'коэффициент_скорости_атаки_%', 'скорость_передвижения'],
        'Дальность атаки': ['мин._дальность_базовой_атаки', 'макс._дальность_базовой_атаки'],
        'Критический урон': ['шанс_крита', 'крит_урон'],
        'Проникновение': ['физ_проникновение', 'маг_проникновение', 'сокращение_перезарядки'],
        'Вампиризм': ['вампиризм', 'вампиризм_навыков'],
        'Защитные характеристики': ['устойчивость', 'уменьшение_крит_урона'],
        'Лечение': ['эффект_лечения', 'полученное_лечение']
    }
    
    for category, attrs in categories.items():
        result += f"\n{category}:\n"
        for attr in attrs:
            if attr in stats:
                result += f"  {attr}: {stats[attr]}\n"
    
    return result

def format_hero_comparison(heroes_data):
    """
    Форматирует сравнение характеристик героев для вывода в Telegram.
    
    Args:
        heroes_data (list): Список кортежей (имя_героя, уровень, характеристики)
    
    Returns:
        str: Отформатированная строка со сравнением
    """
    if not heroes_data or len(heroes_data) < 2:
        return "Недостаточно данных для сравнения героев."
    
    result = "Сравнение героев:\n"
    for hero_name, hero_level, _ in heroes_data:
        result += f"- {hero_name} (уровень {hero_level})\n"
    
    result += "\n"
    
    # Группировка характеристик по категориям
    categories = {
        'Здоровье и мана': ['ОЗ', 'реген_ОЗ', 'мана/энергия', 'реген_маны/энергии'],
        'Атака и защита': ['физ_атака', 'физ_защита', 'маг_защита', 'маг_сила'],
        'Скорость': ['скорость_атаки', 'коэффициент_скорости_атаки_%', 'скорость_передвижения'],
        'Дальность атаки': ['мин._дальность_базовой_атаки', 'макс._дальность_базовой_атаки']
    }
    
    for category, attrs in categories.items():
        result += f"\n{category}:\n"
        for attr in attrs:
            result += f"  {attr}:"
            for _, _, stats in heroes_data:
                if attr in stats:
                    result += f" {stats[attr]} |"
                else:
                    result += " - |"
            result = result[:-2] + "\n"  # Удаляем последний символ "|"
    
    return result

def get_hero_stats_for_tg(hero_name, level=1):
    """
    Получает характеристики героя для Telegram бота.
    
    Args:
        hero_name (str): Имя героя
        level (int): Уровень героя (от 1 до 15)
    
    Returns:
        str: Отформатированная строка с характеристиками
    """
    stats = calculate_hero_stats(hero_name, level)
    return format_hero_stats(stats)

def compare_heroes_for_tg(hero_data_list):
    """
    Сравнивает характеристики героев для Telegram бота.
    
    Args:
        hero_data_list (list): Список кортежей (имя_героя, уровень)
    
    Returns:
        str: Отформатированная строка со сравнением
    """
    heroes_data = []
    for hero_name, level in hero_data_list:
        stats = calculate_hero_stats(hero_name, level)
        if stats:
            heroes_data.append((hero_name, level, stats))
    
    return format_hero_comparison(heroes_data)

# Функции для создания инлайн-клавиатур

def create_role_selection_keyboard():
    """
    Создает инлайн-клавиатуру для выбора роли героя.
    
    Returns:
        types.InlineKeyboardMarkup: Инлайн-клавиатура с ролями
    """
    heroes_by_role = get_heroes_by_role()
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    for role in heroes_by_role.keys():
        callback_data = json.dumps({'action': 'select_role', 'role': role})
        keyboard.add(types.InlineKeyboardButton(text=role, callback_data=callback_data))
    
    return keyboard

def create_heroes_by_role_keyboard(role):
    """
    Создает инлайн-клавиатуру с героями выбранной роли.
    
    Args:
        role (str): Роль героев
    
    Returns:
        types.InlineKeyboardMarkup: Инлайн-клавиатура с героями
    """
    heroes_by_role = get_heroes_by_role()
    
    if role not in heroes_by_role:
        return types.InlineKeyboardMarkup()
    
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    for hero_name in heroes_by_role[role]:
        callback_data = json.dumps({'action': 'select_hero', 'hero': hero_name})
        keyboard.add(types.InlineKeyboardButton(text=hero_name, callback_data=callback_data))
    
    # Кнопка "Назад"
    back_callback = json.dumps({'action': 'back_to_roles'})
    keyboard.add(types.InlineKeyboardButton(text="◀️ Назад к ролям", callback_data=back_callback))
    
    return keyboard

def create_level_selection_keyboard(hero_name):
    """
    Создает инлайн-клавиатуру для выбора уровня героя.
    
    Args:
        hero_name (str): Имя выбранного героя
    
    Returns:
        types.InlineKeyboardMarkup: Инлайн-клавиатура с уровнями
    """
    keyboard = types.InlineKeyboardMarkup(row_width=5)
    
    # Добавляем кнопки с уровнями
    buttons = []
    for level in range(1, 16):
        callback_data = json.dumps({'action': 'select_level', 'hero': hero_name, 'level': level})
        buttons.append(types.InlineKeyboardButton(text=str(level), callback_data=callback_data))
    
    # Разбиваем кнопки на ряды по 5 кнопок
    for i in range(0, len(buttons), 5):
        keyboard.row(*buttons[i:i+5])
    
    # Кнопка "Назад"
    back_callback = json.dumps({'action': 'back_to_heroes'})
    keyboard.add(types.InlineKeyboardButton(text="◀️ Назад к героям", callback_data=back_callback))
    
    return keyboard

def create_comparison_keyboard(hero_name, level):
    """
    Создает инлайн-клавиатуру для сравнения героев.
    
    Args:
        hero_name (str): Имя текущего героя
        level (int): Уровень текущего героя
    
    Returns:
        types.InlineKeyboardMarkup: Инлайн-клавиатура для сравнения
    """
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    
    # Кнопка для сравнения с другим героем
    compare_callback = json.dumps({'action': 'start_compare', 'hero': hero_name, 'level': level})
    keyboard.add(types.InlineKeyboardButton(
        text="Сравнить с другим героем", 
        callback_data=compare_callback
    ))
    
    # Кнопка для изменения уровня
    level_callback = json.dumps({'action': 'change_level', 'hero': hero_name})
    keyboard.add(types.InlineKeyboardButton(
        text="Изменить уровень", 
        callback_data=level_callback
    ))
    
    # Кнопка для выбора другого героя
    back_callback = json.dumps({'action': 'back_to_roles'})
    keyboard.add(types.InlineKeyboardButton(
        text="Выбрать другого героя", 
        callback_data=back_callback
    ))
    
    return keyboard

# Пример использования в обработчиках Telegram бота:
"""
from telebot_hero_stats import (
    get_heroes_list, get_hero_stats_for_tg, compare_heroes_for_tg,
    create_role_selection_keyboard, create_heroes_by_role_keyboard,
    create_level_selection_keyboard, create_comparison_keyboard
)

# Глобальный словарь для хранения состояний пользователей
user_states = {}

# Обработчик команды /hero_stats
@bot.message_handler(commands=['hero_stats'])
def cmd_hero_stats(message):
    keyboard = create_role_selection_keyboard()
    bot.send_message(message.chat.id, "Выберите роль героя:", reply_markup=keyboard)

# Обработчик команды /heroes_list
@bot.message_handler(commands=['heroes_list'])
def cmd_heroes_list(message):
    heroes = get_heroes_list()
    if not heroes:
        bot.send_message(message.chat.id, "Не удалось получить список героев.")
        return
    
    result = "Список доступных героев:\n\n"
    result += "\n".join(heroes)
    bot.send_message(message.chat.id, result)

# Обработчик команды /compare_heroes
@bot.message_handler(commands=['compare_heroes'])
def cmd_compare_heroes(message):
    args = message.text.split()[1:]
    if len(args) < 2 or len(args) % 2 != 0:
        bot.send_message(
            message.chat.id,
            "Пожалуйста, укажите имена героев и их уровни.\n"
            "Пример: /compare_heroes рафаэль 10 тигрил 15"
        )
        return
    
    hero_data_list = []
    for i in range(0, len(args), 2):
        hero_name = args[i]
        try:
            level = int(args[i+1])
            if level < 1 or level > 15:
                bot.send_message(
                    message.chat.id,
                    f"Уровень героя {hero_name} должен быть от 1 до 15"
                )
                return
        except ValueError:
            bot.send_message(
                message.chat.id,
                f"Уровень героя {hero_name} должен быть числом от 1 до 15"
            )
            return
        
        hero_data_list.append((hero_name, level))
    
    result = compare_heroes_for_tg(hero_data_list)
    bot.send_message(message.chat.id, result)

# Обработчик инлайн-кнопок
@bot.callback_query_handler(func=lambda call: True)
def process_callback(call):
    try:
        data = json.loads(call.data)
        action = data.get('action')
        
        if action == 'select_role':
            role = data.get('role')
            keyboard = create_heroes_by_role_keyboard(role)
            bot.edit_message_text(
                f"Выберите героя с ролью {role}:",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=keyboard
            )
        
        elif action == 'back_to_roles':
            keyboard = create_role_selection_keyboard()
            bot.edit_message_text(
                "Выберите роль героя:",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=keyboard
            )
        
        elif action == 'select_hero':
            hero_name = data.get('hero')
            keyboard = create_level_selection_keyboard(hero_name)
            bot.edit_message_text(
                f"Выберите уровень для героя {hero_name}:",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=keyboard
            )
            
            # Сохраняем выбранного героя в состоянии пользователя
            user_id = call.from_user.id
            if user_id not in user_states:
                user_states[user_id] = {}
            user_states[user_id]['selected_hero'] = hero_name
        
        elif action == 'back_to_heroes':
            # Здесь нужно знать, какая роль была выбрана ранее
            # Для простоты вернемся к выбору роли
            keyboard = create_role_selection_keyboard()
            bot.edit_message_text(
                "Выберите роль героя:",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=keyboard
            )
        
        elif action == 'select_level':
            hero_name = data.get('hero')
            level = data.get('level')
            result = get_hero_stats_for_tg(hero_name, level)
            keyboard = create_comparison_keyboard(hero_name, level)
            bot.edit_message_text(
                result,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=keyboard
            )
            
            # Сохраняем выбранный уровень в состоянии пользователя
            user_id = call.from_user.id
            if user_id not in user_states:
                user_states[user_id] = {}
            user_states[user_id]['selected_level'] = level
        
        elif action == 'change_level':
            hero_name = data.get('hero')
            keyboard = create_level_selection_keyboard(hero_name)
            bot.edit_message_text(
                f"Выберите уровень для героя {hero_name}:",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=keyboard
            )
        
        elif action == 'start_compare':
            hero_name = data.get('hero')
            level = data.get('level')
            
            # Сохраняем первого героя для сравнения
            user_id = call.from_user.id
            if user_id not in user_states:
                user_states[user_id] = {}
            user_states[user_id]['compare_hero1'] = hero_name
            user_states[user_id]['compare_level1'] = level
            
            # Переходим к выбору второго героя
            keyboard = create_role_selection_keyboard()
            bot.edit_message_text(
                f"Выберите роль второго героя для сравнения с {hero_name} (уровень {level}):",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=keyboard
            )
            
            # Устанавливаем флаг, что мы в режиме сравнения
            user_states[user_id]['comparing'] = True
        
        # Обработка выбора второго героя для сравнения
        elif action == 'select_level' and user_states.get(call.from_user.id, {}).get('comparing'):
            user_id = call.from_user.id
            hero1_name = user_states[user_id]['compare_hero1']
            hero1_level = user_states[user_id]['compare_level1']
            hero2_name = data.get('hero')
            hero2_level = data.get('level')
            
            # Сравниваем героев
            result = compare_heroes_for_tg([(hero1_name, hero1_level), (hero2_name, hero2_level)])
            
            # Создаем клавиатуру для возврата
            keyboard = types.InlineKeyboardMarkup()
            back_callback = json.dumps({'action': 'back_to_roles'})
            keyboard.add(types.InlineKeyboardButton(
                text="Выбрать других героев", 
                callback_data=back_callback
            ))
            
            bot.edit_message_text(
                result,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=keyboard
            )
            
            # Сбрасываем флаг сравнения
            user_states[user_id]['comparing'] = False
        
        # Отвечаем на callback, чтобы убрать часики
        bot.answer_callback_query(call.id)
        
    except Exception as e:
        print(f"Ошибка при обработке callback: {e}")
        bot.answer_callback_query(call.id, text="Произошла ошибка")
""" 