import logging  # Добавляем импорт logging
import telebot
from telebot import types

# Настраиваем логирование
logger = logging.getLogger(__name__)

def send_menu(bot):
    """
    Отправляет меню бота с кнопками для различных функций.
    
    Args:
        bot: Экземпляр бота telebot
    
    Returns:
        function: Функция-обработчик для команды /menu
    """
    def menu_handler(message):
        # Создаем клавиатуру
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        
        # Кнопки для калькуляторов
        btn_winrate = types.KeyboardButton('/winrate_correction')
        btn_season = types.KeyboardButton('/season_progress')
        btn_rank = types.KeyboardButton('/rank_stars')
        btn_armor = types.KeyboardButton('/armor_and_resistance')
        btn_damage = types.KeyboardButton('/damage_calculator')
        
        # Кнопки для информации о героях
        btn_hero_chars = types.KeyboardButton('/hero_chars')
        btn_chars_table = types.KeyboardButton('/chars_table')
        btn_hero_greed = types.KeyboardButton('/hero_greed')
        btn_hero_tiers = types.KeyboardButton('/hero_tiers')
        btn_hero_stats = types.KeyboardButton('/hero_stats')
        btn_heroes_list = types.KeyboardButton('/heroes_list')
        btn_compare_heroes = types.KeyboardButton('/compare_heroes')
        
        # Другие кнопки
        btn_search = types.KeyboardButton('/search_teammates')
        btn_help = types.KeyboardButton('/help')
        
        # Добавляем кнопки на клавиатуру
        markup.add(
            btn_winrate, btn_season, 
            btn_rank, btn_armor, 
            btn_damage, btn_hero_chars, 
            btn_chars_table, btn_hero_greed, 
            btn_hero_tiers, btn_hero_stats,
            btn_heroes_list, btn_compare_heroes,
            btn_search, btn_help
        )
        
        # Отправляем сообщение с клавиатурой
        bot.send_message(
            message.chat.id, 
            "Выберите функцию из меню:", 
            reply_markup=markup
        )
    
    return menu_handler