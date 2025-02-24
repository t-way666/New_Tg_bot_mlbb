# Константы рангов
RANKS = [
    "Воин",
    "Элита",
    "Мастер",
    "Грандмастер",
    "Эпик",
    "Легенда",
    "Мифический"
]

# Обновленные детали рангов согласно таблице
RANK_DETAILS = {
    "Воин": {"min_level": 3, "stars_per_level": 3, "total_stars": 9},        # 3 уровня * 3 звезды = 9
    "Элита": {"min_level": 3, "stars_per_level": 4, "total_stars": 12},      # 3 уровня * 4 звезды = 12
    "Мастер": {"min_level": 4, "stars_per_level": 4, "total_stars": 16},     # 4 уровня * 4 звезды = 16
    "Грандмастер": {"min_level": 5, "stars_per_level": 5, "total_stars": 25}, # 5 уровней * 5 звезд = 25
    "Эпик": {"min_level": 5, "stars_per_level": 5, "total_stars": 25},       # 5 уровней * 5 звезд = 25
    "Легенда": {"min_level": 5, "stars_per_level": 5, "total_stars": 25}     # 5 уровней * 5 звезд = 25
}                                                                             # Всего = 112 звезд

# Градации мифического ранга
MYTHIC_GRADES = {
    "": (0, 24),        # Просто Мифический
    "Честь": (25, 49),  # Мифическая Честь
    "Слава": (50, 99),  # Мифическая Слава
    "Бессмертный": (100, float('inf'))  # Мифический Бессмертный
}

def get_total_stars_for_rank(rank_name, level=None, mythic_stars=0):
    """Подсчитывает общее количество звезд для достижения ранга"""
    total = sum(details["total_stars"] for rank, details in RANK_DETAILS.items())  # 112 звезд
    
    if rank_name == "Мифический":
        return total + mythic_stars
    return total

def get_rank_and_level(total_stars):
    """Определяет ранг и уровень по количеству звезд"""
    if total_stars >= 112:  # Если достигнут мифический ранг
        mythic_stars = total_stars - 112  # Теперь отнимаем 112 вместо 111
        # Определяем градацию мифического ранга
        for grade, (min_stars, max_stars) in MYTHIC_GRADES.items():
            if min_stars <= mythic_stars <= max_stars:
                if grade:  # Если есть градация (Честь/Слава/Бессмертный)
                    return f"Мифический {grade}", mythic_stars
                else:  # Просто Мифический (0-24 звезды)
                    return "Мифический", mythic_stars
    return "Мифический", total_stars - 112