import diskcache
import redis

from django.conf import settings


redis_connection_pool = redis.ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    db=1)
redis_conn = redis.Redis(connection_pool=redis_connection_pool)

# https://redis.io/topics/lru-cache
redis_conn.config_set("maxmemory", "2gb")
redis_conn.config_set("maxmemory-policy", "volatile-lru")


disk_cache = None
if settings.DISK_CACHE_ENABLE:
    disk_cache = diskcache.Cache("__cache", size_limit=2*(1024**3))  # 2gb
