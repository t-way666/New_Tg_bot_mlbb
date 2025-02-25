import logging  # Добавляем импорт logging

# Настраиваем логирование
logger = logging.getLogger(__name__)

def send_menu(bot):
    @bot.message_handler(commands=['menu'])
    def send_menu_message(message):
        try:
            menu_text = (
                "📋Вот доступные команды:\n\n"
                
                "🚀/start - Старт/рестарт бота\n"
                "📜/menu - Меню доступных команд бота\n"
                "❓/help - Помощь\n\n"
                
                "⭐️/rank_stars - Расчет ранга по звездам и наоборот\n"
                "⚖️/winrate_correction - Корректировка общего винрейта\n"
                "📈/season_progress - Сколько игр нужно сыграть для достижения желаемого ранга\n"
                "🛡/armor_and_resistance - Калькулятор защиты и снижения урона\n"
                "🦸/hero_chars - Информация о героях\n"
                "📊/chars_table - Таблица характеристик героев\n"
                "👥/search_teammates - Поиск тиммейтов для игры\n"
                "🖼/img_creator - Создание изображений для профиля\n\n"
            )

            bot.send_message(
                message.chat.id,
                menu_text,
                parse_mode='HTML'
            )

        except Exception as e:
            logger.error(f"Ошибка в команде menu: {e}")
            bot.reply_to(message, "Произошла ошибка при выполнении команды. Попробуйте позже.")

    return send_menu_message