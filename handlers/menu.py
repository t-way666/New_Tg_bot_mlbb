import logging  # Добавляем импорт logging

# Настраиваем логирование
logger = logging.getLogger(__name__)

def send_menu(bot):
    @bot.message_handler(commands=['menu'])
    def send_menu_message(message):
        try:
            # Сбрасываем состояние пользователя при вызове команды /menu
            try:
                # Получаем текущее состояние пользователя для логирования
                current_state = bot.get_state(message.from_user.id, message.chat.id)
                logger.info(f"Сброс состояния пользователя {message.from_user.id} из состояния {current_state}")
                
                # Сбрасываем состояние
                bot.delete_state(message.from_user.id, message.chat.id)
                logger.info(f"Состояние пользователя {message.from_user.id} успешно сброшено")
            except Exception as state_error:
                logger.error(f"Ошибка при сбросе состояния: {state_error}")
            
            menu_text = """📋 Доступные команды:

🚀 /start - Старт/рестарт бота  
📜 /menu - Меню команд бота  
❓ /help - Помощь  

⭐️ /rank_stars - Расчет ранга по звездам и наоборот  
⚖️ /winrate_correction - Корректировка общего винрейта  
📈 /season_progress - Сколько игр нужно сыграть для достижения желаемого ранга  
🛡 /armor_and_resistance - Калькулятор защиты и снижения урона  
🦸 /hero_chars - Информация о героях  
📊 /chars_table - Таблица характеристик героев  
👥 /search_teammates - Поиск тиммейтов для игры  
"""

            bot.send_message(
                message.chat.id,
                menu_text,
                parse_mode='HTML'
            )

        except Exception as e:
            logger.error(f"Ошибка в команде menu: {e}")
            bot.reply_to(message, "Произошла ошибка при выполнении команды. Попробуйте позже.")

    return send_menu_message