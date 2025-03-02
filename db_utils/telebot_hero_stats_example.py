import telebot
from telebot import types
from telebot_hero_stats import (
    get_heroes_list, get_hero_stats_for_tg, compare_heroes_for_tg,
    create_role_selection_keyboard, create_heroes_by_role_keyboard,
    create_level_selection_keyboard, create_comparison_keyboard
)

# Замените на свой токен
BOT_TOKEN = "YOUR_BOT_TOKEN"
bot = telebot.TeleBot(BOT_TOKEN)

# Глобальный словарь для хранения состояний пользователей
user_states = {}

@bot.message_handler(commands=['start', 'help'])
def cmd_start(message):
    """Обработчик команд /start и /help"""
    help_text = (
        "Привет! Я бот для работы с характеристиками героев MLBB.\n\n"
        "Доступные команды:\n"
        "/hero_stats - Просмотр характеристик героя\n"
        "/heroes_list - Список всех героев\n"
        "/compare_heroes - Сравнение героев (например: /compare_heroes рафаэль 10 тигрил 15)"
    )
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(commands=['hero_stats'])
def cmd_hero_stats(message):
    """Обработчик команды /hero_stats"""
    keyboard = create_role_selection_keyboard()
    bot.send_message(message.chat.id, "Выберите роль героя:", reply_markup=keyboard)

@bot.message_handler(commands=['heroes_list'])
def cmd_heroes_list(message):
    """Обработчик команды /heroes_list"""
    heroes = get_heroes_list()
    if not heroes:
        bot.send_message(message.chat.id, "Не удалось получить список героев.")
        return
    
    result = "Список доступных героев:\n\n"
    result += "\n".join(heroes)
    bot.send_message(message.chat.id, result)

@bot.message_handler(commands=['compare_heroes'])
def cmd_compare_heroes(message):
    """Обработчик команды /compare_heroes"""
    args = message.text.split()[1:]
    if len(args) < 2 or len(args) % 2 != 0:
        bot.send_message(
            message.chat.id,
            "Пожалуйста, укажите имена героев и их уровни.\n"
            "Пример: /compare_heroes рафаэль 10 тигрил 15"
        )
        return
    
    hero_data_list = []
    for i in range(0, len(args), 2):
        hero_name = args[i]
        try:
            level = int(args[i+1])
            if level < 1 or level > 15:
                bot.send_message(
                    message.chat.id,
                    f"Уровень героя {hero_name} должен быть от 1 до 15"
                )
                return
        except ValueError:
            bot.send_message(
                message.chat.id,
                f"Уровень героя {hero_name} должен быть числом от 1 до 15"
            )
            return
        
        hero_data_list.append((hero_name, level))
    
    result = compare_heroes_for_tg(hero_data_list)
    bot.send_message(message.chat.id, result)

@bot.callback_query_handler(func=lambda call: True)
def process_callback(call):
    """Обработчик всех callback-запросов от инлайн-кнопок"""
    try:
        import json
        data = json.loads(call.data)
        action = data.get('action')
        
        if action == 'select_role':
            role = data.get('role')
            keyboard = create_heroes_by_role_keyboard(role)
            bot.edit_message_text(
                f"Выберите героя с ролью {role}:",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=keyboard
            )
        
        elif action == 'back_to_roles':
            keyboard = create_role_selection_keyboard()
            bot.edit_message_text(
                "Выберите роль героя:",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=keyboard
            )
        
        elif action == 'select_hero':
            hero_name = data.get('hero')
            keyboard = create_level_selection_keyboard(hero_name)
            bot.edit_message_text(
                f"Выберите уровень для героя {hero_name}:",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=keyboard
            )
            
            # Сохраняем выбранного героя в состоянии пользователя
            user_id = call.from_user.id
            if user_id not in user_states:
                user_states[user_id] = {}
            user_states[user_id]['selected_hero'] = hero_name
            user_states[user_id]['last_role'] = data.get('role', '')
        
        elif action == 'back_to_heroes':
            # Возвращаемся к выбору героя
            user_id = call.from_user.id
            last_role = user_states.get(user_id, {}).get('last_role', '')
            
            if last_role:
                keyboard = create_heroes_by_role_keyboard(last_role)
                bot.edit_message_text(
                    f"Выберите героя с ролью {last_role}:",
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=keyboard
                )
            else:
                # Если роль не сохранена, возвращаемся к выбору роли
                keyboard = create_role_selection_keyboard()
                bot.edit_message_text(
                    "Выберите роль героя:",
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=keyboard
                )
        
        elif action == 'select_level':
            hero_name = data.get('hero')
            level = data.get('level')
            result = get_hero_stats_for_tg(hero_name, level)
            keyboard = create_comparison_keyboard(hero_name, level)
            bot.edit_message_text(
                result,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=keyboard
            )
            
            # Сохраняем выбранный уровень в состоянии пользователя
            user_id = call.from_user.id
            if user_id not in user_states:
                user_states[user_id] = {}
            user_states[user_id]['selected_level'] = level
        
        elif action == 'change_level':
            hero_name = data.get('hero')
            keyboard = create_level_selection_keyboard(hero_name)
            bot.edit_message_text(
                f"Выберите уровень для героя {hero_name}:",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=keyboard
            )
        
        elif action == 'start_compare':
            hero_name = data.get('hero')
            level = data.get('level')
            
            # Сохраняем первого героя для сравнения
            user_id = call.from_user.id
            if user_id not in user_states:
                user_states[user_id] = {}
            user_states[user_id]['compare_hero1'] = hero_name
            user_states[user_id]['compare_level1'] = level
            
            # Переходим к выбору второго героя
            keyboard = create_role_selection_keyboard()
            bot.edit_message_text(
                f"Выберите роль второго героя для сравнения с {hero_name} (уровень {level}):",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=keyboard
            )
            
            # Устанавливаем флаг, что мы в режиме сравнения
            user_states[user_id]['comparing'] = True
        
        # Обработка выбора второго героя для сравнения
        elif action == 'select_level' and user_states.get(call.from_user.id, {}).get('comparing'):
            user_id = call.from_user.id
            hero1_name = user_states[user_id]['compare_hero1']
            hero1_level = user_states[user_id]['compare_level1']
            hero2_name = data.get('hero')
            hero2_level = data.get('level')
            
            # Сравниваем героев
            result = compare_heroes_for_tg([(hero1_name, hero1_level), (hero2_name, hero2_level)])
            
            # Создаем клавиатуру для возврата
            keyboard = types.InlineKeyboardMarkup()
            back_callback = json.dumps({'action': 'back_to_roles'})
            keyboard.add(types.InlineKeyboardButton(
                text="Выбрать других героев", 
                callback_data=back_callback
            ))
            
            bot.edit_message_text(
                result,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=keyboard
            )
            
            # Сбрасываем флаг сравнения
            user_states[user_id]['comparing'] = False
        
        # Отвечаем на callback, чтобы убрать часики
        bot.answer_callback_query(call.id)
        
    except Exception as e:
        print(f"Ошибка при обработке callback: {e}")
        bot.answer_callback_query(call.id, text="Произошла ошибка")

# Запуск бота
if __name__ == "__main__":
    print("Бот запущен. Нажмите Ctrl+C для остановки.")
    bot.infinity_polling() 