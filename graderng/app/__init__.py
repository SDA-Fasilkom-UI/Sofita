import redis

from django.conf import settings


redis_connection_pool = redis.ConnectionPool(
    host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
