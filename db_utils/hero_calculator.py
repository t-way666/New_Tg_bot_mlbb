import sqlite3
import sys

def calculate_hero_stats(hero_name, level=1):
    """
    Рассчитывает характеристики героя на указанном уровне.
    
    Args:
        hero_name (str): Имя героя
        level (int): Уровень героя (от 1 до 15)
    
    Returns:
        dict: Словарь с характеристиками героя на указанном уровне
    """
    if level < 1 or level > 15:
        print("Уровень должен быть от 1 до 15")
        return None
    
    try:
        # Подключение к базе данных
        conn = sqlite3.connect('../db/characters.db')
        cursor = conn.cursor()
        
        # Поиск героя по имени (нечувствительно к регистру)
        cursor.execute("""
        SELECT id FROM hero_names 
        WHERE LOWER(имя) = LOWER(?)
        """, (hero_name,))
        
        hero_id_result = cursor.fetchone()
        if not hero_id_result:
            print(f"Герой с именем '{hero_name}' не найден.")
            return None
        
        hero_id = hero_id_result[0]
        
        # Получение базовых характеристик героя
        cursor.execute("""
        SELECT * FROM hero_chars_no_up
        WHERE character_id = ?
        """, (hero_id,))
        
        base_stats = cursor.fetchone()
        
        # Получение прироста характеристик героя
        cursor.execute("""
        SELECT * FROM hero_chars_up
        WHERE character_id = ?
        """, (hero_id,))
        
        growth_stats = cursor.fetchone()
        
        # Получение имен столбцов для базовых характеристик
        cursor.execute("PRAGMA table_info(hero_chars_no_up)")
        base_columns = cursor.fetchall()
        base_column_names = [col[1] for col in base_columns]
        
        # Получение имен столбцов для прироста характеристик
        cursor.execute("PRAGMA table_info(hero_chars_up)")
        growth_columns = cursor.fetchall()
        growth_column_names = [col[1] for col in growth_columns]
        
        # Расчет характеристик на указанном уровне
        stats = {}
        
        # Получение имени героя
        cursor.execute("SELECT имя FROM hero_names WHERE id = ?", (hero_id,))
        hero_name_result = cursor.fetchone()
        stats['имя'] = hero_name_result[0]
        stats['уровень'] = level
        
        # Расчет характеристик
        for i in range(1, len(base_stats)):  # Пропускаем character_id
            base_value = base_stats[i]
            
            # Находим соответствующий прирост
            growth_index = -1
            base_col_name = base_column_names[i]
            
            for j in range(1, len(growth_column_names)):
                if growth_column_names[j].replace('прирост_', '') == base_col_name:
                    growth_index = j
                    break
            
            if growth_index != -1 and growth_index < len(growth_stats):
                growth_value = growth_stats[growth_index]
                # Расчет значения на указанном уровне
                value = base_value + growth_value * (level - 1)
                stats[base_col_name] = round(value, 2) if isinstance(value, float) else value
            else:
                stats[base_col_name] = base_value
        
        # Закрытие соединения
        conn.close()
        
        return stats
        
    except sqlite3.Error as e:
        print(f"Ошибка SQLite: {e}")
    except Exception as e:
        print(f"Общая ошибка: {e}")
    
    return None

def print_hero_stats(stats):
    """
    Выводит характеристики героя на экран.
    
    Args:
        stats (dict): Словарь с характеристиками героя
    """
    if not stats:
        return
    
    print(f"\nХарактеристики героя {stats['имя']} на уровне {stats['уровень']}:")
    
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
        print(f"\n{category}:")
        for attr in attrs:
            if attr in stats:
                print(f"  {attr}: {stats[attr]}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Пожалуйста, укажите имя героя и, опционально, уровень.")
        print("Пример: python hero_calculator.py рафаэль 10")
        sys.exit(1)
    
    hero_name = sys.argv[1]
    level = 1
    
    if len(sys.argv) > 2:
        try:
            level = int(sys.argv[2])
        except ValueError:
            print("Уровень должен быть целым числом от 1 до 15")
            sys.exit(1)
    
    stats = calculate_hero_stats(hero_name, level)
    if stats:
        print_hero_stats(stats)