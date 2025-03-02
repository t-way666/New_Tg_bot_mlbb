import sqlite3
import sys
from hero_calculator import calculate_hero_stats

def compare_heroes(hero1_name, hero1_level, hero2_name, hero2_level):
    """
    Сравнивает характеристики двух героев на указанных уровнях.
    
    Args:
        hero1_name (str): Имя первого героя
        hero1_level (int): Уровень первого героя
        hero2_name (str): Имя второго героя
        hero2_level (int): Уровень второго героя
    
    Returns:
        tuple: Кортеж из двух словарей с характеристиками героев
    """
    hero1_stats = calculate_hero_stats(hero1_name, hero1_level)
    hero2_stats = calculate_hero_stats(hero2_name, hero2_level)
    
    return hero1_stats, hero2_stats

def print_comparison(hero1_stats, hero2_stats):
    """
    Выводит сравнение характеристик двух героев.
    
    Args:
        hero1_stats (dict): Характеристики первого героя
        hero2_stats (dict): Характеристики второго героя
    """
    if not hero1_stats or not hero2_stats:
        return
    
    hero1_name = hero1_stats['имя']
    hero1_level = hero1_stats['уровень']
    hero2_name = hero2_stats['имя']
    hero2_level = hero2_stats['уровень']
    
    print(f"\nСравнение героев: {hero1_name} (уровень {hero1_level}) и {hero2_name} (уровень {hero2_level})")
    
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
            if attr in hero1_stats and attr in hero2_stats:
                hero1_value = hero1_stats[attr]
                hero2_value = hero2_stats[attr]
                
                # Определяем, какое значение лучше
                if attr in ['ОЗ', 'реген_ОЗ', 'мана/энергия', 'реген_маны/энергии', 
                           'физ_атака', 'физ_защита', 'маг_защита', 'маг_сила', 
                           'скорость_атаки', 'скорость_передвижения',
                           'мин._дальность_базовой_атаки', 'макс._дальность_базовой_атаки',
                           'шанс_крита', 'крит_урон', 'физ_проникновение', 'маг_проникновение',
                           'сокращение_перезарядки', 'вампиризм', 'вампиризм_навыков',
                           'устойчивость', 'уменьшение_крит_урона', 'эффект_лечения', 'полученное_лечение']:
                    # Для этих атрибутов больше - лучше
                    if hero1_value > hero2_value:
                        comparison = ">"
                    elif hero1_value < hero2_value:
                        comparison = "<"
                    else:
                        comparison = "="
                else:
                    # Для остальных атрибутов просто показываем равенство
                    if hero1_value == hero2_value:
                        comparison = "="
                    else:
                        comparison = "≠"
                
                print(f"  {attr}: {hero1_value} {comparison} {hero2_value}")

def print_multi_hero_comparison(heroes_data):
    """
    Выводит сравнение характеристик нескольких героев.
    
    Args:
        heroes_data (list): Список кортежей (имя_героя, уровень, характеристики)
    """
    if not heroes_data:
        return
    
    # Вывод заголовка
    header = "Характеристика"
    for hero_name, hero_level, _ in heroes_data:
        header += f" | {hero_name} (ур.{hero_level})"
    print(f"\n{header}")
    print("-" * len(header))
    
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
            row = f"{attr}"
            for _, _, stats in heroes_data:
                if attr in stats:
                    row += f" | {stats[attr]}"
                else:
                    row += " | -"
            print(row)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Использование:")
        print("1. Для сравнения двух героев:")
        print("   python hero_comparison.py герой1 уровень1 герой2 уровень2")
        print("   Пример: python hero_comparison.py рафаэль 10 тигрил 15")
        print()
        print("2. Для сравнения нескольких героев:")
        print("   python hero_comparison.py --multi герой1 уровень1 герой2 уровень2 [герой3 уровень3 ...]")
        print("   Пример: python hero_comparison.py --multi рафаэль 10 тигрил 15 лейла 8")
        sys.exit(1)
    
    # Проверяем режим сравнения
    if sys.argv[1] == "--multi":
        # Режим сравнения нескольких героев
        if (len(sys.argv) - 2) % 2 != 0:
            print("Ошибка: для каждого героя должен быть указан уровень")
            sys.exit(1)
        
        heroes_data = []
        for i in range(2, len(sys.argv), 2):
            hero_name = sys.argv[i]
            try:
                hero_level = int(sys.argv[i+1])
                if hero_level < 1 or hero_level > 15:
                    print(f"Ошибка: уровень героя {hero_name} должен быть от 1 до 15")
                    sys.exit(1)
            except ValueError:
                print(f"Ошибка: уровень героя {hero_name} должен быть целым числом")
                sys.exit(1)
            
            stats = calculate_hero_stats(hero_name, hero_level)
            if stats:
                heroes_data.append((hero_name, hero_level, stats))
        
        if heroes_data:
            print_multi_hero_comparison(heroes_data)
    else:
        # Режим сравнения двух героев
        if len(sys.argv) < 5:
            print("Ошибка: необходимо указать имена и уровни двух героев")
            print("Пример: python hero_comparison.py рафаэль 10 тигрил 15")
            sys.exit(1)
        
        hero1_name = sys.argv[1]
        try:
            hero1_level = int(sys.argv[2])
            if hero1_level < 1 or hero1_level > 15:
                print("Уровень первого героя должен быть от 1 до 15")
                sys.exit(1)
        except ValueError:
            print("Уровень первого героя должен быть целым числом")
            sys.exit(1)
        
        hero2_name = sys.argv[3]
        try:
            hero2_level = int(sys.argv[4])
            if hero2_level < 1 or hero2_level > 15:
                print("Уровень второго героя должен быть от 1 до 15")
                sys.exit(1)
        except ValueError:
            print("Уровень второго героя должен быть целым числом")
            sys.exit(1)
        
        hero1_stats, hero2_stats = compare_heroes(hero1_name, hero1_level, hero2_name, hero2_level)
        if hero1_stats and hero2_stats:
            print_comparison(hero1_stats, hero2_stats) 