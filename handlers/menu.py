import logging  # Добавляем импорт logging

# Настраиваем логирование
logger = logging.getLogger(__name__)

def send_menu(bot):
    @bot.message_handler(commands=['menu'])
    def send_menu_message(message):
        try:
            menu_text = (
                "Вот доступные команды:\n\n"
                
                "/start\n"
                "Старт/рестарт бота\n"
                "/menu\n"
                "Меню доступных команд бота\n"
                "/rank\n"
                "Определить ранг по звездам\n"
                "/my_stars\n"
                "Подсчет общего количества звезд\n"
                "/winrate_correction\n"
                "Корректировка винрейта\n"
                "/season_progress\n"
                "Сколько игр нужно сыграть для достижения желаемого ранга\n"
                "/armor_and_resistance\n"
                "Калькулятор защиты и снижения урона\n"
                "/hero_chars\n"
                "Информация о героях\n"
                "/chars_table\n"
                "Таблица характеристик героев\n\n"
                
                "Команды которые в разработке(пока не работают):\n"
                "/help\n"
                "/support\n"
                "/guide\n"
                "/cybersport_info\n"
                "/hero_greed\n"
                "/hero_tiers\n"
                "/search_teammates\n"
                "/img_creator\n"
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