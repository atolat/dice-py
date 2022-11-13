from storage.storage import get_items_from_storage, delete, get_storage_size
import datetime as dt


def expire_sample():
    limit = 20
    count = 0
    for key, val in get_items_from_storage():
        if val.expires_at != -1:
            limit -= 1
            if dt.datetime.fromtimestamp(val.expires_at/1000.0) <= dt.datetime.now():
                delete(key)
                count += 1
        if limit == 0:
            break
    return float(count) / float(20), int(count)


def delete_expired_keys():
    while True:
        deleted_fraction, count_deleted_keys = expire_sample()
        if deleted_fraction < 0.25:
            break
    print(f'Deleted {count_deleted_keys} expired but undeleted keys. Total keys {get_storage_size()}')
