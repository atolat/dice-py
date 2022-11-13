from dataclasses import dataclass
from typing import List


@dataclass
class RedisCommand:
    cmd: str
    args: List[str]
