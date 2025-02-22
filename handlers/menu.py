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
                "/cybersport_info\n"
                "Киберспортивная информация по Mobile Legends\n"
                "/chars_table\n"
                "Таблица характеристик героев\n\n"
                "/search_teammates\n"
                "Поиск тиммейтов для игры\n"
                "/video_guide\n"
                "Видео-гайд по использованию бота\n"
                "/img_creator\n"
                "Создание изображений для профиля\n"
                "/support\n"
                "Поддержка и обратная связь\n\n"
                
                "Команды в разработке:\n"
                "/help\n"
                
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