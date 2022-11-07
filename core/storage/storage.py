import time
from typing import Dict

from core.custom_types.storage_object import StorageObject

hash_table: Dict[str, StorageObject] = {}


def get(key: str) -> StorageObject:
    value = None
    if key in hash_table:
        value = hash_table.get(key)
        if value.expires_at != -1 and value.expires_at <= int(time.time() * 1000):
            delete(key)
            return None
    return value


def put(key: str, value: object, duration_ms: int = -1):
    expires_at = -1
    if duration_ms > 0:
        expires_at = int(time.time() * 1000) + duration_ms
    obj = StorageObject(value, expires_at)
    hash_table[key] = obj


def delete(key: str) -> bool:
    if key in hash_table:
        del (hash_table[key])
        return True
    return False


def get_items_from_storage():
    for key, val in list(hash_table.items()):
        yield key, val


def get_storage_size() -> int:
    return len(hash_table)
