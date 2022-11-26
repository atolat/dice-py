"""
Append Only File Persistence controller
"""

from config import aof_file
from core import resp_encode
from custom_types import StorageObject
from storage import get_items_from_storage


def _encode_key(val: StorageObject) -> str:
    """
    Extracts the string value from storage obj and encodes it as a SET K V statement
    :param val: Redis Storage Object
    :return: RESP encoded set statement
    """
    cmd = f'SET k {val.value}'
    tokens = cmd.split()
    return resp_encode(tokens, is_bulk=True)


def write_aof():
    """
    Appends set statements to the aof file specified in the config
    """
    with open(aof_file, 'wb') as f:
        print(f'Rewriting AOF file at {aof_file}')
        for key, val in get_items_from_storage():
            encoded_command = _encode_key(val)
            f.write(encoded_command)
    print('AOF rewrite complete')


