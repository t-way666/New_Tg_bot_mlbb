from telebot import types
import logging
from utils.stats import stats_manager  # type: ignore # Изменяем импорт

logger = logging.getLogger(__name__)

class GroupHandler:
    _instance = None  # Singleton instance
    
    def __init__(self, bot):
        if GroupHandler._instance is not None:
            raise Exception("GroupHandler уже создан!")
        
        self.bot = bot
        self.group_id = None
        self.media_cache = {}
        GroupHandler._instance = self
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            raise Exception("GroupHandler не инициализирован!")
        return cls._instance
    
    def set_group_id(self, group_id):
        """Установка ID группы"""
        self.group_id = group_id
        logger.info(f"Установлен ID группы: {group_id}")

    def cache_media(self, message):
        """Кэширование медиафайла из группы"""
        try:
            if not message.caption:
                return
                
            # Парсим подпись
            parts = message.caption.replace('/save', '').strip().split('|')
            if len(parts) != 4:
                self.bot.reply_to(message, "Неверный формат. Используйте: /save имя | роль | тип | номер")
                return
                
            hero_name, role, media_type, number = [p.strip().lower() for p in parts]
            
            if message.photo:
                file_id = message.photo[-1].file_id
                media_key = f"{hero_name}_{media_type}_{number}"
                self.media_cache[media_key] = {
                    'file_id': file_id,
                    'type': 'photo',
                    'role': role,
                    'media_type': media_type
                }
            elif message.animation:
                file_id = message.animation.file_id
                media_key = f"{hero_name}_{media_type}_{number}"
                self.media_cache[media_key] = {
                    'file_id': file_id,
                    'type': 'animation',
                    'role': role,
                    'media_type': media_type
                }
                
            self.bot.reply_to(
                message, 
                f"Медиафайл сохранен!\n"
                f"Герой: {hero_name}\n"
                f"Роль: {role}\n"
                f"Тип: {media_type}\n"
                f"Номер: {number}"
            )
        except Exception as e:
            logger.error(f"Ошибка кэширования медиа: {e}")

    def get_hero_media(self, hero_name):
        """Получение медиафайла героя из кэша"""
        return self.media_cache.get(hero_name.lower())

def get_file_from_group(bot, file_id):
    """Получение файла из группы по file_id"""
    try:
        file_info = bot.get_file(file_id)
        return file_info.file_path
    except Exception as e:
        logger.error(f"Ошибка получения файла: {e}")
        return None

def is_admin(bot, chat_id, user_id):
    """Проверка прав администратора"""
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['creator', 'administrator']
    except Exception as e:
        logger.error(f"Ошибка проверки прав администратора: {e}")
        return False

def register_group_handlers(bot):
    @bot.message_handler(commands=['setup'], func=lambda message: message.chat.type == 'group')
    def setup_group(message):
        """Настройка группы для бота"""
        group_handler = GroupHandler.get_instance()
        if group_handler:
            group_handler.set_group_id(message.chat.id)
            bot.reply_to(message, "✅ Группа успешно настроена для работы с ботом!")
        else:
            bot.reply_to(message, "❌ Ошибка: обработчик группы не инициализирован")

    @bot.message_handler(content_types=['photo', 'animation'], chat_types=['group'])
    def handle_media(message):
        """Обработка медиафайлов в группе"""
        if not is_admin(bot, message.chat.id, message.from_user.id):
            bot.reply_to(message, "❌ Только администраторы могут сохранять медиафайлы")
            return
            
        group_handler = GroupHandler.get_instance()
        if not group_handler:
            return
            
        if message.caption and message.caption.startswith('/save'):
            group_handler.cache_media(message)

    @bot.message_handler(commands=['stats'], chat_types=['group'])
    def show_stats(message):
        """Показать статистику использования бота"""
        stats = stats_manager.get_stats(message.chat.id)  # Используем напрямую stats_manager
        bot.reply_to(message, stats)

    @bot.message_handler(commands=['help'], chat_types=['group'])
    def group_help(message):
        """Помощь по командам в группе"""
        help_text = (
            "Команды для группы:\n"
            "/save - сохранить медиафайл (в подписи укажите имя_героя)\n"
            "/stats - показать статистику\n"
            "/help - это сообщение"
        )
        bot.reply_to(message, help_text)