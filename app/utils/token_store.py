# app/utils/token_store.py
from app.core.redis import redis_client
from datetime import timedelta

TOKEN_BLACKLIST_PREFIX = "jwt_blacklist:"

def blacklist_token(jti: str, exp_seconds: int):
    """Lưu token vào blacklist trong Redis"""
    redis_client.setex(f"{TOKEN_BLACKLIST_PREFIX}{jti}", timedelta(seconds=exp_seconds), "true")

def is_token_blacklisted(jti: str) -> bool:
    return redis_client.exists(f"{TOKEN_BLACKLIST_PREFIX}{jti}") == 1
