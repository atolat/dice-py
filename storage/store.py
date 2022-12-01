import datetime as dt
from ctypes import c_uint8
from typing import Dict

from config.config import key_limit, eviction_strategy, eviction_ratio
from core.stats import key_space
from custom_types import StorageObject
from storage import eviction_pool
from utils.time_utils import get_current_clock

_hash_table: Dict[str, StorageObject] = {}

# Auxiliary dictionary that stores objects with expiry
_expires_table: Dict[StorageObject, int] = {}


def new_storage_object(value: object, duration_ms: int = -1, o_type: c_uint8 = 0,
                       o_encoding: c_uint8 = 0) -> StorageObject:
    expires_at = -1
    obj = StorageObject(value=value, expires_at=expires_at, type_encoding=o_type | o_encoding,
                        last_accessed_at=get_current_clock())
    if duration_ms > 0:
        expires_at = duration_ms
        set_expiry(obj, expires_at)
    return obj


def get(key: str) -> StorageObject:
    value = None
    if key in _hash_table:
        value = _hash_table.get(key)
        if has_expired(value):
            delete(key)
            return None
        value.last_accessed_at = get_current_clock()
    return value


def set_expiry(obj: StorageObject, expiry_duration_ms: int):
    _expires_table[obj] = int(dt.datetime.now().timestamp() * 1000) + int(expiry_duration_ms)


def has_expired(obj: StorageObject) -> bool:
    if obj not in _expires_table:
        return False
    return _expires_table[obj] <= int(dt.datetime.now().timestamp() * 1000)


def get_expiry(obj: StorageObject) -> int:
    if obj in _expires_table:
        return _expires_table[obj]
    return -1


def put(key: str, obj: StorageObject):
    # Try to evict before putting
    if get_storage_size() > key_limit:
        print("Keys exceeded size, triggering eviction")
        evict()
    # Add last accessed time to object
    obj.last_accessed_at = get_current_clock()
    _hash_table[key] = obj
    # TODO: Make this more robust, this is a temporary hack
    if 'keys' in key_space[0]:
        key_space[0]['keys'] += 1
    else:
        key_space[0]['keys'] = 1


def delete(key: str) -> bool:
    if key in _hash_table:
        print('Grabbing object')
        obj = _hash_table[key]
        print(f'got object to delete {obj}, deleting...')
        try:
            del _hash_table[key]
            del _expires_table[obj]
        except KeyError:
            # Suppress key error
            pass
        key_space[0]['keys'] -= 1
        return True
    return False


def get_items_from_storage():
    for key, val in list(_hash_table.items()):
        yield key, val


def get_keys_from_storage():
    for key in list(_hash_table):
        yield key


def get_random_key():
    return next(iter(_hash_table))


def get_storage_size() -> int:
    return len(_hash_table)


##########################################
# Eviction Handlers
# TODO: Move this to a different module!
##########################################

# Simple - delete the first key
def evict_first():
    for k in get_keys_from_storage():
        delete(k)
        return


# Evict keys at random
def evict_all_keys_random():
    evict_count = int(eviction_ratio * key_limit)
    while evict_count > 0:
        key = get_random_key()
        delete(key)
        evict_count -= 1


# Approximated LRU
def populate_eviction_pool():
    sample_size = 5
    # while sample_size > 0:
    for key in _hash_table:
        # key = get_random_key()
        print(f'Sampling {key}')
        obj = _hash_table[key]
        print(f'Sampled -- {key}::{obj.value}')
        eviction_pool.push(key, obj.last_accessed_at)
        sample_size -= 1
        if sample_size <= 0:
            break


def evict_all_keys_LRU():
    print('Populating eviction pool')
    populate_eviction_pool()
    print(f'Pool populated with {eviction_pool.size()} elements')
    evict_count = int(eviction_ratio * key_limit)
    print(f'Evicting {evict_count} keys')
    while evict_count > 0 and eviction_pool.size() > 0:
        print(f'Getting item from pool')
        item = eviction_pool.pop()
        print(f'got {item.key}')
        if item is None:
            return
        print(f'deleting {item.key}')
        delete(item.key)
        evict_count -= 1


def evict():
    match eviction_strategy:
        case 'simple-first':
            return evict_first()
        case 'allkeys-random':
            return evict_all_keys_random()
        case 'allkeys-lru':
            return evict_all_keys_LRU()
        case _:
            pass
