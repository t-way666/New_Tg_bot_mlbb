def send_help(bot):
    @bot.message_handler(commands=['help'])
    def send_help_message(message):
        help_text = """
🔹 FAQ - частые вопросы  
🔹 Видео инструкция по использованию бота  

🔹 SUPPORT - поддержка  
  ◽️ [Оставить отзыв](https://t.me/T_w_a_y)  
  ◽️ [Сообщить об ошибке](https://t.me/T_w_a_y)  
  ◽️ [Поддержать проект](https://t.me/T_w_a_y)  
  ◽️ [Связаться с разработчиками](https://t.me/T_w_a_y)  
"""
        
        bot.reply_to(message, help_text)
    return send_help_message