import telebot

def send_help(bot):
    """
    Отправляет справочную информацию о командах бота.
    
    Args:
        bot: Экземпляр бота telebot
    
    Returns:
        function: Функция-обработчик для команды /help
    """
    def help_handler(message):
        help_text = (
            "Доступные команды:\n\n"
            "/start - Начать работу с ботом\n"
            "/menu - Показать меню бота\n"
            "/help - Показать эту справку\n\n"
            
            "Калькуляторы:\n"
            "/winrate_correction - Калькулятор винрейта\n"
            "/season_progress - Калькулятор прогресса сезона\n"
            "/rank_stars - Калькулятор звезд ранга\n"
            "/armor_and_resistance - Калькулятор защиты и снижения урона\n"
            "/damage_calculator - Калькулятор урона\n\n"
            
            "Информация о героях:\n"
            "/hero_chars - Характеристики героя\n"
            "/chars_table - Таблица характеристик героев\n"
            "/hero_greed - Жадность героя\n"
            "/hero_tiers - Тир-лист героев\n"
            "/hero_stats - Статистика героя на разных уровнях\n"
            "/heroes_list - Список всех героев\n"
            "/compare_heroes - Сравнение героев (например: /compare_heroes рафаэль 10 тигрил 15)\n\n"
            
            "Другое:\n"
            "/search_teammates - Поиск тиммейтов"
        )
        bot.send_message(message.chat.id, help_text)
    
    return help_handler