# Константы рангов
RANKS = [
    {"name": "Воин", "levels": 3, "stars_per_level": 3},
    {"name": "Элита", "levels": 4, "stars_per_level": 3},
    {"name": "Мастер", "levels": 4, "stars_per_level": 4},
    {"name": "Грандмастер", "levels": 5, "stars_per_level": 4},
    {"name": "Эпик", "levels": 5, "stars_per_level": 5},
    {"name": "Легенда", "levels": 5, "stars_per_level": 5},
    {"name": "Мифический", "levels": 1, "stars_per_level": 100}
]

MYTHICAL_RANKS = {
    0: "Мифический",
    25: "Мифическая честь",
    50: "Мифическая слава",
    100: "Мифический бессмертный"
}

def get_total_stars_for_rank(rank_name):
    """Подсчитывает общее количество звезд для достижения ранга"""
    total = 0
    for rank in RANKS:
        if rank["name"] == rank_name:
            return total + (rank["levels"] * rank["stars_per_level"])
        total += rank["levels"] * rank["stars_per_level"]
    return total

def get_rank_and_level(stars):
    """Определяет ранг и уровень по количеству звезд"""
    s = stars
    for rank in RANKS:
        total = rank["levels"] * rank["stars_per_level"]
        if s < total:
            level = rank["levels"] - (s // rank["stars_per_level"])
            stars_in_level = s % rank["stars_per_level"]
            return rank["name"], level, stars_in_level
        s -= total
    
    # Определение мифического ранга
    for threshold, rank_name in sorted(MYTHICAL_RANKS.items(), reverse=True):
        if s >= threshold:
            return rank_name, None, s
    
    return MYTHICAL_RANKS[0], None, s