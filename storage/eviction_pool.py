from dataclasses import dataclass
from typing import List, Dict

from utils import get_idle_time


@dataclass
class PoolItem:
    key: str
    last_accessed_at: int

    def __lt__(self, other):
        get_idle_time(self.last_accessed_at) < get_idle_time(other.last_accessed_at)


_pool: List[PoolItem] = []
_key_set: Dict[str, PoolItem] = {}
_e_pool_max_size = 16


def push(key, last_accessed_at):
    global _pool
    print(f'Pushing item with key {key} and last access {last_accessed_at}')
    # Check if key is in pool
    if key in _key_set:
        return
    else:
        # Create a pool item
        p_item = PoolItem(key, last_accessed_at)
        print(f'Created pool item {p_item}')
        # Check if pool has space for the new candidate
        if len(_pool) < _e_pool_max_size:
            _key_set[key] = p_item
            _pool.append(p_item)
            _pool = sorted(_pool)
        # Pool is full
        else:
            # Check the access time of the current candidate and see if it is greater that the worst (last
            # element of the pool)
            if last_accessed_at > _pool[0].last_accessed_at:
                _pool = _pool[1:]
                _key_set[key] = p_item
                _pool = _pool.append(p_item)


def pop() -> PoolItem:
    global _pool
    if len(_pool) == 0:
        return None
    p_item = _pool[0]
    _pool = _pool[1:]
    del _key_set[p_item.key]
    return p_item


def size():
    global _pool
    return len(_pool)


