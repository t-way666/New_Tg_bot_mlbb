from typing import Dict, Callable
import logging
from handlers import armor_and_resistance, hero_chars

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
                "Информация о героях\n\n"
                
                "Команды которые в разработке(пока не работают):\n"
                "/help\n"
                "/support\n"
                "/guide\n"
                "/cybersport_info\n"
                "/chars_table\n"
                "/hero_greed\n"
                "/hero_tiers\n"
                "/search_teammates\n"
                "/img_creator\n"
            ),
            '/help': lambda m: bot.send_message(m.chat.id, "Используйте /menu для списка команд"),
            '/rank': lambda m: bot.send_message(m.chat.id, "Используйте /menu для списка команд"),
            '/my_stars': lambda m: bot.send_message(m.chat.id, "Используйте /menu для списка команд"),
            '/winrate_correction': lambda m: bot.send_message(m.chat.id, "Используйте /menu для списка команд"),
            '/season_progress': lambda m: bot.send_message(m.chat.id, "Используйте /menu для списка команд"),
            '/armor_and_resistance': lambda m: armor_and_resistance.armor_calculator(m, bot),
            '/hero_chars': lambda m: hero_chars.register_hero_handlers(bot)(m)  # Исправляем имя команды
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