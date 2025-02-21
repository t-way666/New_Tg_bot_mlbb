import sqlite3
import logging

logger = logging.getLogger(__name__)

class DBEditor:
    def __init__(self, db_path='characters.db'):  # Убираем 'db/' из пути
        self.db_path = db_path

    def add_hero(self, hero_data):
        """Добавление нового героя"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Добавляем имя героя
            cursor.execute(
                "INSERT INTO hero_names (имя) VALUES (?)",
                (hero_data['name'],)
            )
            hero_id = cursor.lastrowid
            
            # Добавляем роли
            cursor.execute(
                """INSERT INTO hero_role 
                (character_id, убийца, стрелок, маг, танк, боец, поддержка) 
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (hero_id, *[hero_data['roles'].get(role, False) 
                for role in ['убийца', 'стрелок', 'маг', 'танк', 'боец', 'поддержка']])
            )
            
            conn.commit()
            logger.info(f"Герой {hero_data['name']} успешно добавлен")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Ошибка при добавлении героя: {e}")
        finally:
            conn.close()

    def update_hero(self, hero_name, updates):
        """Обновление данных героя"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Получаем id героя
            cursor.execute("SELECT id FROM hero_names WHERE имя=?", (hero_name,))
            hero_id = cursor.fetchone()
            
            if hero_id:
                hero_id = hero_id[0]
                # Обновляем роли если они указаны
                if 'roles' in updates:
                    roles = updates['roles']
                    set_clause = ', '.join([f"{k}=?" for k in roles.keys()])
                    cursor.execute(
                        f"UPDATE hero_role SET {set_clause} WHERE character_id=?",
                        (*roles.values(), hero_id)
                    )
                
                conn.commit()
                logger.info(f"Герой {hero_name} успешно обновлен")
            else:
                logger.warning(f"Герой {hero_name} не найден")
                
        except Exception as e:
            conn.rollback()
            logger.error(f"Ошибка при обновлении героя: {e}")
        finally:
            conn.close()

    def delete_hero(self, hero_name):
        """Удаление героя"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM hero_names WHERE имя=?", (hero_name,))
            
            if cursor.rowcount > 0:
                conn.commit()
                logger.info(f"Герой {hero_name} успешно удален")
            else:
                logger.warning(f"Герой {hero_name} не найден")
                
        except Exception as e:
            conn.rollback()
            logger.error(f"Ошибка при удалении героя: {e}")
        finally:
            conn.close()

# Пример использования:
if __name__ == "__main__": 
    db = DBEditor()
    
    # Добавление нового героя
    new_hero = {
        'name': 'новый_герой',
        'roles': {
            'убийца': True,
            'стрелок': False,
            'маг': False,
            'танк': False,
            'боец': True,
            'поддержка': False
        }
    }
    db.add_hero(new_hero)
    
    # Обновление существующего героя
    updates = {
        'roles': {
            'убийца': False,
            'стрелок': True
        }
    }
    db.update_hero('мия', updates)
    
    # Удаление героя
    db.delete_hero('старый_герой')