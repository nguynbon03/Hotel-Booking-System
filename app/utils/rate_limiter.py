"""
Simple Redis-based rate limiting utility.

Functions in this module help protect sensitive routes such as email
verification and password reset from being spammed. A key is provided
for each action/user and a limit with a period is enforced.
"""
from app.core.redis import redis_main

def is_rate_limited(key: str, limit: int, period: int) -> bool:
    """
    Return True if the given key has exceeded the allowed number of
    operations within the specified period. Otherwise increment the count
    and return False.
    """
    count = redis_main.get(key)
    if count is None:
        # First call, set the TTL and count
        redis_main.setex(key, period, 1)
        return False
    try:
        current = int(count)
    except (TypeError, ValueError):
        redis_main.setex(key, period, 1)
        return False
    if current < limit:
        redis_main.incr(key)
        return False
    return True
