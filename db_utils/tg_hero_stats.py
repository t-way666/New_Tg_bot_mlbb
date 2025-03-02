from hero_calculator import calculate_hero_stats
import sqlite3

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

# Пример использования в обработчиках Telegram бота:
"""
from tg_hero_stats import get_heroes_list, get_hero_stats_for_tg, compare_heroes_for_tg

# Обработчик команды /hero_stats
@dp.message_handler(commands=['hero_stats'])
async def cmd_hero_stats(message: types.Message):
    args = message.get_args().split()
    if len(args) < 1:
        await message.answer("Пожалуйста, укажите имя героя и, опционально, уровень.\n"
                            "Пример: /hero_stats рафаэль 10")
        return
    
    hero_name = args[0]
    level = 1
    
    if len(args) > 1:
        try:
            level = int(args[1])
            if level < 1 or level > 15:
                await message.answer("Уровень должен быть от 1 до 15")
                return
        except ValueError:
            await message.answer("Уровень должен быть числом от 1 до 15")
            return
    
    result = get_hero_stats_for_tg(hero_name, level)
    await message.answer(result)

# Обработчик команды /compare_heroes
@dp.message_handler(commands=['compare_heroes'])
async def cmd_compare_heroes(message: types.Message):
    args = message.get_args().split()
    if len(args) < 2 or len(args) % 2 != 0:
        await message.answer("Пожалуйста, укажите имена героев и их уровни.\n"
                            "Пример: /compare_heroes рафаэль 10 тигрил 15")
        return
    
    hero_data_list = []
    for i in range(0, len(args), 2):
        hero_name = args[i]
        try:
            level = int(args[i+1])
            if level < 1 or level > 15:
                await message.answer(f"Уровень героя {hero_name} должен быть от 1 до 15")
                return
        except ValueError:
            await message.answer(f"Уровень героя {hero_name} должен быть числом от 1 до 15")
            return
        
        hero_data_list.append((hero_name, level))
    
    result = compare_heroes_for_tg(hero_data_list)
    await message.answer(result)

# Обработчик команды /heroes_list
@dp.message_handler(commands=['heroes_list'])
async def cmd_heroes_list(message: types.Message):
    heroes = get_heroes_list()
    if not heroes:
        await message.answer("Не удалось получить список героев.")
        return
    
    result = "Список доступных героев:\n\n"
    result += "\n".join(heroes)
    await message.answer(result)
""" 