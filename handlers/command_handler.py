from typing import Dict, Callable
import logging
from handlers import (
    armor_and_resistance, 
    hero_chars, 
    cybersport_info, 
    hero_tiers,
    hero_greed,  # Добавляем новый импорт
    search_teammates,  # Добавляем новый импорт
    video_guide_bot,  # Добавляем новый импорт
    img_creator,  # Добавляем новый импорт
    support  # Добавляем новый импорт
)

logger = logging.getLogger(__name__)

def handle_commands(bot, message):
    """Обработчик команд бота"""
    try:
        command_handlers = {
            '/start': lambda m: bot.send_message(
                m.chat.id, 
                "👋 Привет! Я помогу тебе с расчетами в Mobile Legends.\n"
                "Используй команду /menu чтобы увидеть список доступных команд."
            ),
            '/menu': lambda m: bot.send_message(
                m.chat.id,
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
                "/hero\n"
                "Информация о героях\n"
                "/cybersport_info\n"
                "Информация о киберспортивной сцене MLBB\n"
                "/hero_tiers\n"
                "Тир-листы героев\n"
                "/hero_greed\n"
                "Рейтинг жадности героев\n\n"
                
                "Команды которые в разработке(пока не работают):\n"
                "/help\n"
                "/support\n"
                "/guide\n"
                "/chars_table\n"
                "/search_teammates\n"
                "/img_creator\n"
            ),
            '/help': lambda m: bot.send_message(m.chat.id, "Используйте /menu для списка команд"),
            '/rank': lambda m: bot.send_message(m.chat.id, "Используйте /menu для списка команд"),
            '/my_stars': lambda m: bot.send_message(m.chat.id, "Используйте /menu для списка команд"),
            '/winrate_correction': lambda m: bot.send_message(m.chat.id, "Используйте /menu для списка команд"),
            '/season_progress': lambda m: bot.send_message(m.chat.id, "Используйте /menu для списка команд"),
            '/armor_and_resistance': lambda m: armor_and_resistance.armor_calculator(m, bot),
            '/hero_chars': lambda m: hero_chars.register_hero_handlers(bot)(m),
            '/cybersport_info': lambda m: cybersport_info.register_cybersport_handlers(bot)(m),
            '/hero_tiers': lambda m: hero_tiers.register_hero_tiers(bot)(m),
            '/hero_greed': lambda m: hero_greed.register_hero_greed_handlers(bot)(m),  # Добавляем новый обработчик
            '/search_teammates': lambda m: search_teammates.register_handlers(bot)(m),
            '/video_guide': lambda m: video_guide_bot.register_handlers(bot)(m),
            '/img_creator': lambda m: img_creator.register_handlers(bot)(m),
            '/support': lambda m: support.register_handlers(bot)(m),
        }

        command = message.text.split()[0].lower()
        handler = command_handlers.get(command)

        if handler:
            logger.info(f"Выполняется команда: {command}")
            handler(message)
        else:
            logger.warning(f"Неизвестная команда: {command}")
            bot.reply_to(
                message,
                "Неизвестная команда. Используйте /menu для списка доступных команд."
            )

    except Exception as e:
        logger.error(f"Ошибка при обработке команды {message.text}: {e}")
        bot.reply_to(
            message,
            "Произошла ошибка при выполнении команды. Используйте /menu для списка команд."
        )