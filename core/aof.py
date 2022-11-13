from config.config import aof_file
from core import resp_encode
from custom_types import StorageObject
from storage import get_items_from_storage


def _encode_key(key, val: StorageObject):
    cmd = f'SET k {val.value}'
    tokens = cmd.split()
    return resp_encode(tokens, is_bulk=True)


def write_aof():
    # TODO -- Catch exception here
    with open(aof_file, 'wb') as f:
        print(f'Rewriting AOF file at {aof_file}')
        for key, val in get_items_from_storage():
            encoded_command = _encode_key(key, val)
            f.write(encoded_command)
    print('AOF rewrite complete')


