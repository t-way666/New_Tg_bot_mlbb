import pandas as pd
import sqlite3
import os

# Создание папки для базы данных, если она не существует
os.makedirs('db', exist_ok=True)

# Загрузка данных из CSV файла
df = pd.read_csv('db/characters.csv')

# Создание подключения к базе данных SQLite
conn = sqlite3.connect('db/characters.db')
cursor = conn.cursor()

# Удаление таблиц, если они уже существуют
cursor.execute('DROP TABLE IF EXISTS hero_chars_up')
cursor.execute('DROP TABLE IF EXISTS hero_chars_no_up')
cursor.execute('DROP TABLE IF EXISTS hero_role')
cursor.execute('DROP TABLE IF EXISTS hero_names')

# Создание таблицы для персонажей
cursor.execute('''
CREATE TABLE IF NOT EXISTS hero_names (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    имя TEXT
)
''')

# Вставка данных из DataFrame в таблицу hero_names
df_heroes = df[['имя']].drop_duplicates()
for _, row in df_heroes.iterrows():
    cursor.execute('INSERT INTO hero_names (имя) VALUES (?)', (row['имя'],))

conn.commit()

# Получение ID персонажей
character_ids = pd.read_sql_query('SELECT id, имя FROM hero_names', conn)

# Создание таблицы для ролей
cursor.execute('''
CREATE TABLE IF NOT EXISTS hero_role (
    "character_id" INTEGER,
    "убийца" BOOLEAN,
    "стрелок" BOOLEAN,
    "маг" BOOLEAN,
    "танк" BOOLEAN,
    "боец" BOOLEAN,
    "поддержка" BOOLEAN,
    FOREIGN KEY(character_id) REFERENCES hero_names(id)
)
''')

# Вставка данных из DataFrame в таблицу hero_role
df_roles = df[['имя', 'убийца', 'стрелок', 'маг', 'танк', 'боец', 'поддержка']]
df_roles = df_roles.merge(character_ids, on='имя')
for _, row in df_roles.iterrows():
    cursor.execute('''
        INSERT INTO hero_role (character_id, убийца, стрелок, маг, танк, боец, поддержка)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (row['id'], row['убийца'], row['стрелок'], row['маг'], row['танк'], row['боец'], row['поддержка']))

conn.commit()

# Создание таблицы для характеристик без прироста
cursor.execute('''
CREATE TABLE IF NOT EXISTS hero_chars_no_up (
    "character_id" INTEGER,
    "ОЗ" INTEGER,
    "реген_ОЗ" REAL,
    "мана/энергия" INTEGER,
    "реген_маны/энергии" REAL,
    "физ_атака" INTEGER,
    "физ_защита" INTEGER,
    "маг_защита" INTEGER,
    "скорость_атаки" REAL,
    "маг_сила" INTEGER,
    "коэффициент_скорости_атаки_%" INTEGER,
    "скорость_передвижения" INTEGER,
    "мин._дальность_базовой_атаки" REAL,
    "макс._дальность_базовой_атаки" REAL,
    "шанс_крита" INTEGER,
    "крит_урон" INTEGER,
    "сокращение_перезарядки" INTEGER,
    "физ_проникновение" INTEGER,
    "маг_проникновение" INTEGER,
    "вампиризм" INTEGER,
    "вампиризм_навыков" INTEGER,
    "устойчивость" INTEGER,
    "уменьшение_крит_урона" INTEGER,
    "эффект_лечения" INTEGER,
    "полученное_лечение" INTEGER,
    FOREIGN KEY(character_id) REFERENCES hero_names(id)
)
''')

# Вставка данных из DataFrame в таблицу hero_chars_no_up
df_attributes_no_up = df[['имя', 'ОЗ', 'реген_ОЗ', 'мана/энергия', 'реген_маны/энергии', 'физ_атака', 'физ_защита', 'маг_защита', 'скорость_атаки', 'маг_сила', 'коэффициент_скорости_атаки_%', 'скорость_передвижения', 'мин._дальность_базовой_атаки', 'макс._дальность_базовой_атаки', 'шанс_крита', 'крит_урон', 'сокращение_перезарядки', 'физ_проникновение', 'маг_проникновение', 'вампиризм', 'вампиризм_навыков', 'устойчивость', 'уменьшение_крит_урона', 'эффект_лечения', 'полученное_лечение']]
df_attributes_no_up = df_attributes_no_up.merge(character_ids, on='имя')
for _, row in df_attributes_no_up.iterrows():
    cursor.execute('''
        INSERT INTO hero_chars_no_up (
            character_id, ОЗ, реген_ОЗ, "мана/энергия", "реген_маны/энергии",
            физ_атака, физ_защита, маг_защита, скорость_атаки, маг_сила,
            "коэффициент_скорости_атаки_%", скорость_передвижения,
            "мин._дальность_базовой_атаки", "макс._дальность_базовой_атаки",
            шанс_крита, крит_урон, сокращение_перезарядки, физ_проникновение,
            маг_проникновение, вампиризм, вампиризм_навыков, устойчивость,
            уменьшение_крит_урона, эффект_лечения, полученное_лечение
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (row['id'], row['ОЗ'], row['реген_ОЗ'], row['мана/энергия'], row['реген_маны/энергии'],
          row['физ_атака'], row['физ_защита'], row['маг_защита'], row['скорость_атаки'],
          row['маг_сила'], row['коэффициент_скорости_атаки_%'], row['скорость_передвижения'],
          row['мин._дальность_базовой_атаки'], row['макс._дальность_базовой_атаки'],
          row['шанс_крита'], row['крит_урон'], row['сокращение_перезарядки'],
          row['физ_проникновение'], row['маг_проникновение'], row['вампиризм'],
          row['вампиризм_навыков'], row['устойчивость'], row['уменьшение_крит_урона'],
          row['эффект_лечения'], row['полученное_лечение']))

conn.commit()

# Создание таблицы для характеристик с приростом
cursor.execute('''
CREATE TABLE IF NOT EXISTS hero_chars_up (
    "character_id" INTEGER,
    "прирост_ОЗ" INTEGER,
    "прирост_реген_ОЗ" REAL,
    "прирост_мана/энергия" INTEGER,
    "прирост_реген_маны/энергии" REAL,
    "прирост_физ_атака" REAL,
    "прирост_физ_защита" REAL,
    "прирост_маг_защита" REAL,
    "прирост_скорость_атаки" REAL,
    FOREIGN KEY(character_id) REFERENCES hero_names(id)
)
''')

# Вставка данных в таблицу hero_chars_up
df_attributes_up = df[['имя', 'прирост_ОЗ', 'прирост_реген_ОЗ', 'прирост_мана/энергия', 'прирост_реген_маны/энергии', 'прирост_физ_атака', 'прирост_физ_защита', 'прирост_маг_защита', 'прирост_скорость_атаки']]
df_attributes_up = df_attributes_up.merge(character_ids, on='имя')
for _, row in df_attributes_up.iterrows():
    cursor.execute('''
        INSERT INTO hero_chars_up (
            character_id, прирост_ОЗ, прирост_реген_ОЗ, "прирост_мана/энергия",
            "прирост_реген_маны/энергии", прирост_физ_атака, прирост_физ_защита,
            прирост_маг_защита, прирост_скорость_атаки
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (row['id'], row['прирост_ОЗ'], row['прирост_реген_ОЗ'],
          row['прирост_мана/энергия'], row['прирост_реген_маны/энергии'],
          row['прирост_физ_атака'], row['прирост_физ_защита'],
          row['прирост_маг_защита'], row['прирост_скорость_атаки']))

conn.commit()

# Пример запроса для добавления новой записи
new_character = {
    "имя": 'новый_герой'
}

# Вставка новой записи в таблицу hero_names
columns = ', '.join([f'"{col}"' for col in new_character.keys()])
placeholders = ', '.join('?' * len(new_character))
sql = f'INSERT INTO hero_names ({columns}) VALUES ({placeholders})'
cursor.execute(sql, tuple(new_character.values()))

# Получение ID новой записи
new_character_id = cursor.lastrowid

# Вставка новой записи в таблицу hero_role
new_roles = {
    "character_id": new_character_id,
    "убийца": False,
    "стрелок": False,
    "маг": True,
    "танк": False,
    "боец": False,
    "поддержка": True
}

columns = ', '.join([f'"{col}"' for col in new_roles.keys()])
placeholders = ', '.join('?' * len(new_roles))
sql = f'INSERT INTO hero_role ({columns}) VALUES ({placeholders})'
cursor.execute(sql, tuple(new_roles.values()))

# Вставка новой записи в таблицу hero_chars_no_up
new_attributes_no_up = {
    "character_id": new_character_id,
    "ОЗ": 2500,
    "реген_ОЗ": 7.0,
    "мана/энергия": 500,
    "реген_маны/энергии": 4,
    "физ_атака": 120,
    "физ_защита": 15,
    "маг_защита": 15,
    "скорость_атаки": 1.0,
    "маг_сила": 0,
    "коэффициент_скорости_атаки_%": 100,
    "скорость_передвижения": 240,
    "мин._дальность_базовой_атаки": 4.5,
    "макс._дальность_базовой_атаки": 4.5,
    "шанс_крита": 0,
    "крит_урон": 200,
    "сокращение_перезарядки": 0,
    "физ_проникновение": 0,
    "маг_проникновение": 0,
    "вампиризм": 0,
    "вампиризм_навыков": 0,
    "устойчивость": 0,
    "уменьшение_крит_урона": 0,
    "эффект_лечения": 0,
    "полученное_лечение": 0
}

columns = ', '.join([f'"{col}"' for col in new_attributes_no_up.keys()])
placeholders = ', '.join('?' * len(new_attributes_no_up))
sql = f'INSERT INTO hero_chars_no_up ({columns}) VALUES ({placeholders})'
cursor.execute(sql, tuple(new_attributes_no_up.values()))

# Вставка новой записи в таблицу hero_chars_up
new_attributes_up = {
    "character_id": new_character_id,
    "прирост_ОЗ": 150,
    "прирост_реген_ОЗ": 0.30,
    "прирост_мана/энергия": 100,
    "прирост_реген_маны/энергии": 0.2,
    "прирост_физ_атака": 7.0,
    "прирост_физ_защита": 4.0,
    "прирост_маг_защита": 2.5,
    "прирост_скорость_атаки": 0.01
}

columns = ', '.join([f'"{col}"' for col in new_attributes_up.keys()])
placeholders = ', '.join('?' * len(new_attributes_up))
sql = f'INSERT INTO hero_chars_up ({columns}) VALUES ({placeholders})'
cursor.execute(sql, tuple(new_attributes_up.values()))

# Сохранение изменений и закрытие подключения
conn.commit()
conn.close()