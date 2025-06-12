import random

def get_random(min: float = 0, max: float = 1) -> float:
    return min+(max-min)*random.random()