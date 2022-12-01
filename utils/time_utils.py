import datetime as dt


def get_current_clock() -> int:
    return int(int(dt.datetime.now().timestamp()) & 0x00FFFFFF)


def get_idle_time(last_accessed_at: int) -> int:
    c = get_current_clock()
    if c >= last_accessed_at:
        return c - last_accessed_at
    return (0x00FFFFFF - last_accessed_at) + c
