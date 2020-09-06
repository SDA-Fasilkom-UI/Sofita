import diskcache
import redis

from django.conf import settings


redis_connection_pool = redis.ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    db=1)

disk_cache = diskcache.Cache("__cache")
