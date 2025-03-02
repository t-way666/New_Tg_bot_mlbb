import sqlite3
import sys

def get_hero_info(hero_name):
    try:
        # Подключение к базе данных
        conn = sqlite3.connect('db/characters.db')
        cursor = conn.cursor()
        
        # Поиск героя по имени (нечувствительно к регистру)
        cursor.execute("""
        SELECT id FROM hero_names 
        WHERE LOWER(имя) = LOWER(?)
        """, (hero_name,))
        
        hero_id_result = cursor.fetchone()
        if not hero_id_result:
            print(f"Герой с именем '{hero_name}' не найден.")
            return
        
        hero_id = hero_id_result[0]
        
        # Получение базовой информации о герое
        cursor.execute("""
        SELECT hn.имя, 
               CASE WHEN hr.убийца = 1 THEN 'Убийца' ELSE '' END,
               CASE WHEN hr.стрелок = 1 THEN 'Стрелок' ELSE '' END,
               CASE WHEN hr.маг = 1 THEN 'Маг' ELSE '' END,
               CASE WHEN hr.танк = 1 THEN 'Танк' ELSE '' END,
               CASE WHEN hr.боец = 1 THEN 'Боец' ELSE '' END,
               CASE WHEN hr.поддержка = 1 THEN 'Поддержка' ELSE '' END
        FROM hero_names hn
        JOIN hero_role hr ON hn.id = hr.character_id
        WHERE hn.id = ?
        """, (hero_id,))
        
        basic_info = cursor.fetchone()
        
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
        
        # Вывод информации о герое
        print(f"\nИнформация о герое: {basic_info[0]}")
        
        # Вывод ролей
        roles = [role for role in basic_info[1:] if role]
        print(f"Роли: {', '.join(roles)}")
        
        print("\nБазовые характеристики:")
        for i in range(1, len(base_stats)):  # Пропускаем character_id
            print(f"  {base_column_names[i]}: {base_stats[i]}")
        
        print("\nПрирост характеристик:")
        for i in range(1, len(growth_stats)):  # Пропускаем character_id
            print(f"  {growth_column_names[i]}: {growth_stats[i]}")
        
        # Закрытие соединения
        conn.close()
        
    except sqlite3.Error as e:
        print(f"Ошибка SQLite: {e}")
    except Exception as e:
        print(f"Общая ошибка: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        hero_name = sys.argv[1]
        get_hero_info(hero_name)
    else:
        print("Пожалуйста, укажите имя героя в качестве аргумента.")
        print("Пример: python hero_info.py рафаэль") 