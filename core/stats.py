key_space = [{} for _ in range(4)]


def update_db_stat(num: int, metric: str, value: int):
    key_space[num][metric] = value
