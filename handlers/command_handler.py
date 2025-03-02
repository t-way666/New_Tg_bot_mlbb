from typing import Dict, Callable
import logging
from handlers import (
    armor_and_resistance, 
    hero_chars, 
    hero_tiers,
    hero_greed,
    search_teammates,
    chars_table,
    damage_calculator,
)

logger = logging.getLogger(__name__)

COMMANDS = {
    'start': 'Начать работу с ботом',
    'help': 'Показать справку',
    'winrate_correction': 'Корректировка винрейта',
    'season_progress': 'Прогресс сезона',
    'rank_stars': 'Расчет ранга по звездам и наоборот',
    'menu': 'Открыть главное меню',
    'hero_chars': 'Характеристики героев',
    'chars_table': 'Таблица характеристик',
    'hero_greed': 'Грид героев',
    'hero_tiers': 'Тир-лист героев',
    'search_teammates': 'Поиск тиммейтов',
    'armor_and_resistance': 'Калькулятор защиты и снижения урона',
    'damage_calculator': 'Калькулятор урона с учетом всех модификаторов',
}

def handle_commands(bot, message):
    """Обработчик команд бота"""
    try:
        # Сбрасываем состояние пользователя при получении любой команды
        try:
            current_state = bot.get_state(message.from_user.id, message.chat.id)
            if current_state:
                logger.info(f"Обработчик команд: Сброс состояния пользователя {message.from_user.id} из состояния {current_state}")
                bot.delete_state(message.from_user.id, message.chat.id)
                logger.info(f"Обработчик команд: Состояние пользователя {message.from_user.id} успешно сброшено")
        except Exception as state_error:
            logger.error(f"Обработчик команд: Ошибка при сбросе состояния: {state_error}")
        
        command = message.text.split()[0].lower()
        logger.info(f"Обработчик команд: Получена команда {command} от пользователя {message.from_user.id}")
        
        command_handlers = {
            '/start': lambda m: bot.send_message(
                m.chat.id, 
                "👋 Привет! Я помогу тебе с расчетами в Mobile Legends.\n"
                "Используй команду /menu чтобы увидеть список доступных команд."
            ),
            '/menu': lambda m: handle_menu_command(bot, m),
            '/help': lambda m: bot.send_message(m.chat.id, "Используйте /menu для списка команд"),
            '/rank_stars': lambda m: bot.send_message(m.chat.id, "Используйте /menu для списка команд"),
            '/winrate_correction': lambda m: bot.send_message(m.chat.id, "Используйте /menu для списка команд"),
            '/season_progress': lambda m: bot.send_message(m.chat.id, "Используйте /menu для списка команд"),
            '/chars_table': lambda m: chars_table.register_handlers(bot)(m),
            '/hero_chars': lambda m: hero_chars.register_hero_handlers(bot)(m),
            '/hero_tiers': lambda m: hero_tiers.register_hero_tiers_handlers(bot)(m),
            '/hero_greed': lambda m: hero_greed.register_hero_greed_handlers(bot)(m),
            '/search_teammates': lambda m: search_teammates.register_handlers(bot)(m),
        }

        # Специальная обработка для команды /armor_and_resistance
        if command == '/armor_and_resistance':
            logger.info(f"Специальная обработка команды /armor_and_resistance для пользователя {message.from_user.id}")
            try:
                # Отправляем простое сообщение для подтверждения получения команды
                bot.send_message(message.chat.id, "Запускаю калькулятор защиты и снижения урона...")
                logger.info(f"Отправлено подтверждающее сообщение пользователю {message.from_user.id}")
                
                # Вызываем функцию armor_calculator
                armor_and_resistance.armor_calculator(message, bot)
                logger.info(f"Функция armor_calculator успешно вызвана для пользователя {message.from_user.id}")
            except Exception as e:
                logger.error(f"Ошибка при обработке команды /armor_and_resistance: {e}")
                bot.send_message(
                    message.chat.id,
                    "Произошла ошибка при запуске калькулятора защиты. Пожалуйста, попробуйте позже."
                )
            return
            
        # Специальная обработка для команды /damage_calculator
        if command == '/damage_calculator':
            logger.info(f"Специальная обработка команды /damage_calculator для пользователя {message.from_user.id}")
            try:
                # Отправляем простое сообщение для подтверждения получения команды
                bot.send_message(message.chat.id, "Запускаю калькулятор урона...")
                logger.info(f"Отправлено подтверждающее сообщение пользователю {message.from_user.id}")
                
                # Вызываем функцию damage_calculator
                damage_calculator.damage_calc(message, bot)
                logger.info(f"Функция damage_calc успешно вызвана для пользователя {message.from_user.id}")
            except Exception as e:
                logger.error(f"Ошибка при обработке команды /damage_calculator: {e}")
                bot.send_message(
                    message.chat.id,
                    "Произошла ошибка при запуске калькулятора урона. Пожалуйста, попробуйте позже."
                )
            return

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

def handle_menu_command(bot, message):
    """Специальный обработчик для команды /menu с сбросом состояний"""
    try:
        # Сбрасываем состояние пользователя
        try:
            current_state = bot.get_state(message.from_user.id, message.chat.id)
            if current_state:
                logger.info(f"Сброс состояния пользователя {message.from_user.id} из состояния {current_state}")
                bot.delete_state(message.from_user.id, message.chat.id)
                logger.info(f"Состояние пользователя {message.from_user.id} успешно сброшено")
        except Exception as state_error:
            logger.error(f"Ошибка при сбросе состояния: {state_error}")
        
        # Отправляем меню
        menu_text = """📋 Доступные команды:

🚀 /start - Старт/рестарт бота  
📜 /menu - Меню команд бота  
❓ /help - Помощь  

⭐️ /rank_stars - Расчет ранга по звездам и наоборот  
⚖️ /winrate_correction - Корректировка общего винрейта  
📈 /season_progress - Сколько игр нужно сыграть для достижения желаемого ранга  
🛡 /armor_and_resistance - Калькулятор защиты и снижения урона  
💥 /damage_calculator - Калькулятор урона с учетом всех модификаторов  
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
        logger.error(f"Ошибка при обработке команды /menu: {e}")
        bot.reply_to(
            message,
            "Произошла ошибка при выполнении команды. Попробуйте позже."
        )