from ctypes import c_uint8
from typing import Dict
import datetime as dt

from config import eviction_ratio, key_limit, eviction_strategy
from config.config import key_limit
from core.stats import key_space
from custom_types import StorageObject

_hash_table: Dict[str, StorageObject] = {}


def new_storage_object(value: object, duration_ms: int = -1, o_type: c_uint8 = 0,
                       o_encoding: c_uint8 = 0) -> StorageObject:
    expires_at = -1
    if duration_ms > 0:
        expires_at = int(dt.datetime.now().timestamp() * 1000) + duration_ms
    return StorageObject(value=value, expires_at=expires_at, type_encoding=o_type | o_encoding)


def get(key: str) -> StorageObject:
    value = None
    if key in _hash_table:
        value = _hash_table.get(key)
        if value.expires_at != -1 and value.expires_at <= int(dt.datetime.now().timestamp() * 1000):
            delete(key)
            return None
    return value


def put(key: str, obj: StorageObject):
    # Try to evict before putting
    if get_storage_size() > key_limit:
        evict()
    _hash_table[key] = obj
    # TODO: Make this more robust, this is a temporary hack
    if 'keys' in key_space[0]:
        key_space[0]['keys'] += 1
    else:
        key_space[0]['keys'] = 1


def delete(key: str) -> bool:
    if key in _hash_table:
        del (_hash_table[key])
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


def evict_first():
    for k in get_keys_from_storage():
        delete(k)
        return


def evict_all_keys_random():
    evict_count = int(eviction_ratio * key_limit)
    while evict_count >= 0:
        key = get_random_key()
        delete(key)
        evict_count -= 1


def evict():
    match eviction_strategy:
        case 'simple-first':
            return evict_first()
        case 'allkeys-random':
            return evict_all_keys_random()
        case _:
            pass
