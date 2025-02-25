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
    "Воин": {
        "min_level": 3,  # Начинаем с уровня 3
        "max_level": 1,  # Заканчиваем уровнем 1
        "stars_per_level": 3,  # 3 звезды на уровень
        "total_stars": 9  # Всего в ранге
    },
    "Элита": {
        "min_level": 3,
        "max_level": 1,
        "stars_per_level": 4,
        "total_stars": 12
    },
    "Мастер": {
        "min_level": 4,
        "max_level": 1,
        "stars_per_level": 4,
        "total_stars": 16
    },
    "Грандмастер": {
        "min_level": 5,
        "max_level": 1,
        "stars_per_level": 5,
        "total_stars": 25
    },
    "Эпик": {
        "min_level": 5,
        "max_level": 1,
        "stars_per_level": 5,
        "total_stars": 25
    },
    "Легенда": {
        "min_level": 5,
        "max_level": 1,
        "stars_per_level": 5,
        "total_stars": 25
    },
    "Мифический": {
        "min_level": 1,
        "max_level": 1,
        "stars_per_level": 0,
        "total_stars": 0
    }
}

# Градации мифического ранга
MYTHIC_GRADES = {
    "": (0, 24),        # Просто Мифический
    "Честь": (25, 49),  # Мифическая Честь
    "Слава": (50, 99),  # Мифическая Слава
    "Бессмертный": (100, float('inf'))  # Мифический Бессмертный
}

def get_total_stars_for_rank(rank_name, level, stars=0):
    """
    Подсчитывает общее количество звезд для достижения ранга и уровня
    """
    if rank_name == "Мифический":
        return 112 + stars  # 112 звезд до мифического + мифические звезды

    total = 0
    current_rank_found = False

    # Проходим по всем рангам до текущего
    for rank in RANKS:
        if rank == "Мифический":
            break
            
        if rank == rank_name:
            current_rank_found = True
            details = RANK_DETAILS[rank]
            
            # Если это начальная точка
            if rank == "Воин" and level == 3 and stars == 0:
                return 0
                
            # Считаем звезды в текущем ранге
            # От минимального уровня до текущего
            for curr_level in range(details["min_level"], level - 1, -1):
                total += details["stars_per_level"]
            total += stars  # Добавляем текущие звезды
            break
            
        if not current_rank_found:
            # Добавляем все звезды предыдущих рангов
            total += RANK_DETAILS[rank]["total_stars"]
            
    return total

def get_rank_and_level(total_stars):
    """
    Определяет ранг и уровень по общему количеству звезд
    """
    if total_stars >= 112:  # Мифический ранг
        mythic_stars = total_stars - 112
        for grade, (min_stars, max_stars) in MYTHIC_GRADES.items():
            if min_stars <= mythic_stars <= max_stars:
                if grade:  # Если есть градация (Честь/Слава/Бессмертный)
                    return f"Мифический {grade}", mythic_stars
                return "Мифический", mythic_stars
        return "Мифический Бессмертный", mythic_stars

    stars_left = total_stars
    for rank in RANKS:
        if rank == "Мифический":
            break
            
        details = RANK_DETAILS[rank]
        if stars_left < details["total_stars"]:
            # Определяем уровень в текущем ранге
            current_stars = 0
            for level in range(details["min_level"], details["max_level"] - 1, -1):
                stars_for_level = details["stars_per_level"]
                if stars_left < stars_for_level:
                    return rank, level
                stars_left -= stars_for_level
        stars_left -= details["total_stars"]

    return "Воин", 3  # Начальный ранг