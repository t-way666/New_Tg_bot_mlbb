from typing import Dict, Callable
import logging
from handlers import armor_and_resistance

logger = logging.getLogger(__name__)

def handle_commands(bot, message):
    """Обработчик команд бота"""
    try:
        command_handlers = {
            '/start': lambda m: bot.send_message(
                m.chat.id, 
                "👋 Привет! Я помогу тебе с расчетами в Mobile Legends.\n"
                "Вот доступные команды:\n\n"
                "🎮 /rank - Определить ранг по звездам\n"
                "⭐ /my_stars - Подсчет общего количества звезд\n"
                "📊 /winrate_correction - Корректировка винрейта\n"
                "📈 /season_progress - Прогресс сезона\n"
                "🛡️ /armor_and_resistance - Калькулятор защиты\n"
            ),
            '/help': lambda m: bot.send_message(m.chat.id, "Используйте /start для списка команд"),
            '/rank': lambda m: bot.send_message(m.chat.id, "Используйте /start для списка команд"),
            '/my_stars': lambda m: bot.send_message(m.chat.id, "Используйте /start для списка команд"),
            '/winrate_correction': lambda m: bot.send_message(m.chat.id, "Используйте /start для списка команд"),
            '/season_progress': lambda m: bot.send_message(m.chat.id, "Используйте /start для списка команд"),
            '/armor_and_resistance': lambda m: armor_and_resistance.armor_calculator(m, bot)
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
                "Неизвестная команда. Используйте /start для списка доступных команд."
            )

    except Exception as e:
        logger.error(f"Ошибка при обработке команды {message.text}: {e}")
        bot.reply_to(
            message,
            "Произошла ошибка при выполнении команды. Используйте /start для списка команд."
        )