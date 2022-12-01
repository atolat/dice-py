"""
Handles deletion of expired keys
"""
from typing import Tuple

from storage import get_items_from_storage, delete, get_storage_size, has_expired
import datetime as dt


def _expire_sample() -> Tuple[float, int]:
    """
    Samples 20 keys, checks if they are expired and deletes them
    :return: fraction of deleted keys (expired), total keys
    """
    limit = 20
    count = 0
    for key, val in get_items_from_storage():
        if val.expires_at != -1:
            limit -= 1
            if has_expired(val):
                delete(key)
                count += 1
        if limit == 0:
            break
    return float(count) / float(20), int(count)


def delete_expired_keys():
    """
    This function is triggered periodically.
    It samples a small number of keys in the store and deletes 25% of the sampled keys every run.i
    """
    while True:
        deleted_fraction, count_deleted_keys = _expire_sample()
        if deleted_fraction < 0.25:
            break
    print(f'Deleted {count_deleted_keys} expired but undeleted keys. Total keys {get_storage_size()}')
