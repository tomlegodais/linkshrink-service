import random


def select_random_sampling(item: str, length: int) -> str:
    if len(item) < length:
        raise ValueError("Length of item must be greater than length of sampling")

    positions = random.sample(range(len(item)), length)
    return ''.join([item[i] for i in positions])
