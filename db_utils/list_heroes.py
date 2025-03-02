import sqlite3

try:
    # Подключение к базе данных
    conn = sqlite3.connect('db/characters.db')
    cursor = conn.cursor()
    
    # Получение списка героев с их ролями
    cursor.execute("""
    SELECT hn.id, hn.имя, 
           CASE WHEN hr.убийца = 1 THEN 'Убийца' ELSE '' END,
           CASE WHEN hr.стрелок = 1 THEN 'Стрелок' ELSE '' END,
           CASE WHEN hr.маг = 1 THEN 'Маг' ELSE '' END,
           CASE WHEN hr.танк = 1 THEN 'Танк' ELSE '' END,
           CASE WHEN hr.боец = 1 THEN 'Боец' ELSE '' END,
           CASE WHEN hr.поддержка = 1 THEN 'Поддержка' ELSE '' END
    FROM hero_names hn
    JOIN hero_role hr ON hn.id = hr.character_id
    ORDER BY hn.имя
    """)
    
    heroes = cursor.fetchall()
    
    # Группировка героев по ролям
    heroes_by_role = {
        'Убийца': [],
        'Стрелок': [],
        'Маг': [],
        'Танк': [],
        'Боец': [],
        'Поддержка': []
    }
    
    # Вывод списка всех героев
    print(f"Всего героев в базе данных: {len(heroes)}")
    
    for hero in heroes:
        hero_id = hero[0]
        hero_name = hero[1]
        roles = [role for role in hero[2:] if role]
        
        # Добавление героя в соответствующие категории
        for role in roles:
            heroes_by_role[role].append(hero_name)
        
        print(f"{hero_id}. {hero_name} - {', '.join(roles)}")
    
    # Вывод количества героев по ролям
    print("\nКоличество героев по ролям:")
    for role, heroes_list in heroes_by_role.items():
        print(f"{role}: {len(heroes_list)}")
        
    # Закрытие соединения
    conn.close()
    
except sqlite3.Error as e:
    print(f"Ошибка SQLite: {e}")
except Exception as e:
    print(f"Общая ошибка: {e}") 