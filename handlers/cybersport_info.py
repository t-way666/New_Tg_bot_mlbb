from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command("cybersport_info"))
async def cybersport_info(message: types.Message):
    text = """
🏆 *Киберспортивная информация по Mobile Legends*

📱 *Официальные ресурсы:*
• [Официальный сайт MLBB Esports](https://www.ml.mobilelegends.com/en)
• [MLBB Esports Twitter](https://twitter.com/MLBBEsports)

📺 *YouTube каналы:*
• [Mobile Legends Esports](https://youtube.com/c/MLBBEsports)
• [MLBB Russia](https://youtube.com/@MobilelegendsRussia)
• [NAVI MLBB](https://youtube.com/@navimilbb)

💬 *Telegram каналы:*
• [ML News](https://t.me/mobilelegendsru)
• [MLBB Pro Scene](https://t.me/mlbbproscene)
• [ML Tournaments](https://t.me/mltournaments)

👨‍🏫 *Тренеры и аналитики:*
• [Coach BTK](https://youtube.com/@CoachBTK)
• [ML Guide](https://youtube.com/@MLGuide)

🎮 *Развлекательный контент:*
• [Hororo Chan](https://youtube.com/@HororoChan) - обзоры обновлений
• [Shinmen Takezo](https://youtube.com/@ShinmenTakezo) - геймплей и гайды
• [Elgin](https://youtube.com/@ElginMLBB) - новости и анализ

📊 *Полезные ресурсы:*
• [Статистика героев](https://m.mobilelegends.com/en/rank)
• [MLBB Wiki](https://mobile-legends.fandom.com/)
• [ML Guide Website](https://www.mlguide.org)

🔍 *Турнирные платформы:*
• [ESL Play](https://play.eslgaming.com/mobilelegends)
• [Mobile Legends Community](https://www.mobilelegends.com/en/newsdetail/1351)
"""
    await message.answer(text, parse_mode="Markdown", disable_web_page_preview=True)
