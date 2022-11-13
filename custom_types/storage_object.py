from dataclasses import dataclass


@dataclass
class StorageObject:
    value: object
    expires_at: int
