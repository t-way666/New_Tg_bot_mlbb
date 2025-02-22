from telebot.handler_backends import State, StatesGroup
from telebot.types import Message
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging

def register_cybersport_handlers(bot):
    logger = logging.getLogger(__name__)
    logger.info(f"Регистрация обработчика cybersport_info")

    def cybersport_info_handler(message: Message):
        text = """
🏆 *Киберспортивная информация по Mobile Legends*

📱 *Официальные ресурсы:*
• [Официальный сайт MLBB Esports](https://www.ml.mobilelegends.com/en)
• [MLBB Esports Twitter](https://twitter.com/MLBBEsports)
• [MLBB Esports Instagram](https://www.instagram.com/mlbb.esports)
• [M5 World Championship](https://m5.mobilelegends.com)

📺 *YouTube каналы:*
• [Mobile Legends Esports](https://youtube.com/c/MLBBEsports) - официальный канал
• [MLBB Russia](https://youtube.com/@MobilelegendsRussia) - русскоязычный канал
• [NAVI MLBB](https://youtube.com/@navimilbb) - канал команды NAVI
• [MPL Indonesia](https://youtube.com/@MPLindonesia) - крупнейшая региональная лига
• [ONE Esports](https://youtube.com/@ONEEsports) - турнирный организатор

💬 *Telegram каналы и чаты:*
• [ML News](https://t.me/mobilelegendsru) - новости и обновления
• [MLBB Pro Scene](https://t.me/mlbbproscene) - про-сцена
• [ML Tournaments](https://t.me/mltournaments) - турниры
• [MLBB Russia Community](https://t.me/mlbbru) - русскоязычное сообщество
• [ML Tournaments Chat](https://t.me/mltournamentsChat) - чат о турнирах

👨‍🏫 *Тренеры и аналитики:*
• [Coach BTK](https://youtube.com/@CoachBTK) - тренер команды BTK
• [ML Guide](https://youtube.com/@MLGuide) - гайды и обучение
• [AssassinDave](https://youtube.com/@AssassinDave) - анализ мета
• [Gemik](https://youtube.com/@GemikOfficial) - профессиональный игрок
• [Zeys](https://youtube.com/@zeysmlbb) - тир-листы и анализ героев

🎮 *Развлекательный контент:*
• [Hororo Chan](https://youtube.com/@HororoChan) - обзоры обновлений
• [Shinmen Takezo](https://youtube.com/@ShinmenTakezo) - геймплей и гайды
• [Elgin](https://youtube.com/@ElginMLBB) - новости и анализ
• [Betosky](https://youtube.com/@Betosky) - образовательный контент
• [Gosu General](https://youtube.com/@GosuGeneralTV) - стримы и геймплей

📊 *Полезные ресурсы:*
• [Статистика героев](https://m.mobilelegends.com/en/rank)
• [MLBB Wiki](https://mobile-legends.fandom.com/)
• [ML Guide Website](https://www.mlguide.org)
• [Liquipedia MLBB](https://liquipedia.net/mobilelegends)
• [Natan.gg](https://www.natan.gg) - статистика и аналитика

🔍 *Турнирные платформы:*
• [ESL Play](https://play.eslgaming.com/mobilelegends)
• [Mobile Legends Community](https://www.mobilelegends.com/en/newsdetail/1351)
• [MLBB Esports](https://esports.mobilelegends.com)
• [Challengermode](https://www.challengermode.com/games/mlbb)
• [Toornament](https://www.toornament.com/games/mobilelegends)
"""
        bot.send_message(message.chat.id, text, parse_mode="Markdown", disable_web_page_preview=True)

    return cybersport_info_handler  # Возвращаем функцию-обработчик
