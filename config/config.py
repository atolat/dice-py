# Host & port that run the redis server -- default: localhost:56789
host = '0.0.0.0'
port = 56789

# TCP mode
# - async - handles multiple concurrent clients
# - sync - handles a single client
mode = 'async'

# Number of keys in the DB, crossing this limit triggers an eviction
key_limit = 3

# % of keys to evict with the random eviction strategy
eviction_ratio = 0.40

# Supported Strategies
# - simple-first
# - allkeys-random
eviction_strategy = 'allkeys-lru'

# Persistence file path
aof_file = './dice-master.aof'

# Interval between automatic deletions
delete_frequency = 100000  # in milliseconds
