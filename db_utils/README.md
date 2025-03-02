# Утилиты для работы с базой данных героев MLBB

В этой директории находятся утилиты для работы с базой данных героев игры Mobile Legends: Bang Bang (MLBB).

## Файлы

- `db_summary.md` - описание структуры базы данных и рекомендации по ее использованию
- `hero_info.py` - скрипт для получения информации о конкретном герое
- `list_heroes.py` - скрипт для вывода списка всех героев с их ролями
- `hero_calculator.py` - скрипт для расчета характеристик героя на указанном уровне
- `hero_comparison.py` - скрипт для сравнения характеристик нескольких героев на разных уровнях
- `hero_stats_gui.py` - графический интерфейс для работы с характеристиками героев
- `telebot_hero_stats.py` - модуль для интеграции функционала расчета характеристик героев в Telegram бот (telebot)

## Использование

### Получение информации о герое

```bash
python hero_info.py <имя_героя>
```

Пример:
```bash
python hero_info.py рафаэль
```

### Получение списка всех героев

```bash
python list_heroes.py
```

### Расчет характеристик героя на указанном уровне

```bash
python hero_calculator.py <имя_героя> <уровень>
```

Пример:
```bash
python hero_calculator.py рафаэль 10
```

### Сравнение двух героев на разных уровнях

```bash
python hero_comparison.py <герой1> <уровень1> <герой2> <уровень2>
```

Пример:
```bash
python hero_comparison.py рафаэль 10 тигрил 15
```

### Сравнение нескольких героев на разных уровнях

```bash
python hero_comparison.py --multi <герой1> <уровень1> <герой2> <уровень2> [<герой3> <уровень3> ...]
```

Пример:
```bash
python hero_comparison.py --multi рафаэль 10 тигрил 15 лейла 8
```

### Графический интерфейс для работы с характеристиками героев

```bash
python hero_stats_gui.py
```

Графический интерфейс позволяет:
- Выбрать героя и уровень для просмотра его характеристик
- Добавлять героев с разными уровнями в список для сравнения
- Сравнивать характеристики нескольких героев на разных уровнях

### Интеграция с Telegram ботом (telebot)

Модуль `telebot_hero_stats.py` предоставляет функции для интеграции с Telegram ботом:

- Получение списка героев
- Получение характеристик героя на указанном уровне
- Сравнение характеристик нескольких героев
- Создание инлайн-клавиатур для удобного взаимодействия

Пример использования в Telegram боте:

```python
from telebot import TeleBot
from telebot_hero_stats import (
    get_heroes_list, get_hero_stats_for_tg, compare_heroes_for_tg,
    create_role_selection_keyboard
)

bot = TeleBot("YOUR_BOT_TOKEN")

# Глобальный словарь для хранения состояний пользователей
user_states = {}

@bot.message_handler(commands=['hero_stats'])
def cmd_hero_stats(message):
    keyboard = create_role_selection_keyboard()
    bot.send_message(message.chat.id, "Выберите роль героя:", reply_markup=keyboard)

# Другие обработчики...

bot.polling()
```

## Структура базы данных

Подробное описание структуры базы данных и рекомендации по ее использованию находятся в файле `db_summary.md`. 