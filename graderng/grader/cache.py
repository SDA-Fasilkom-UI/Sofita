import datetime
import os

import redis

from django.conf import settings

from app import disk_cache, redis_connection_pool
from grader.utils import get_tc_path

redis_conn = redis.Redis(connection_pool=redis_connection_pool)


class RedisCacheManager():

    EXPIRE_TIME = settings.REDIS_CACHE_EXPIRE_TIME

    def __init__(self, problem_name, tc, cases_path=None):
        self.cases_path = cases_path
        self.problem_name = problem_name
        self.tc = tc

    def insert(self, in_gzip, out_gzip):
        in_time, out_time = self.get_tc_actual_time()

        in_time_key, out_time_key = self.get_time_key()
        in_key, out_key = self.get_key()
        redis_conn.hmset(self.get_hash_name(), {
            in_time_key: in_time,
            out_time_key: out_time,
            in_key: in_gzip,
            out_key: out_gzip
        })

        expire_time = datetime.timedelta(days=self.EXPIRE_TIME)
        redis_conn.expire(self.get_hash_name(), expire_time)

    def exists(self):
        in_time, out_time = self.get_tc_actual_time()
        cache_in_time, cache_out_time = self.get_time_content()

        if (cache_in_time is None) or (cache_out_time is None):
            return False

        if (in_time > cache_in_time) or (out_time > cache_out_time):
            return False

        return True

    def get_content(self):
        return redis_conn.hmget(self.get_hash_name(), self.get_key())

    def get_time_content(self):
        in_time, out_time = redis_conn.hmget(
            self.get_hash_name(), self.get_time_key())

        if in_time is not None:
            in_time = int(in_time)

        if out_time is not None:
            out_time = int(out_time)

        return in_time, out_time

    def get_key(self):
        in_key = "TC-IN_{}-{}".format(self.problem_name, self.tc)
        out_key = "TC-OUT_{}-{}".format(self.problem_name, self.tc)
        return in_key, out_key

    def get_time_key(self):
        in_time_key = "TC-IN-TIME_{}-{}".format(self.problem_name, self.tc)
        out_time_key = "TC-OUT-TIME_{}-{}".format(self.problem_name, self.tc)
        return in_time_key, out_time_key

    def get_hash_name(self):
        return "TC_{}-{}".format(self.problem_name, self.tc)

    def get_tc_actual_time(self):
        if self.cases_path is None:
            raise RedisCacheManagerException("Cases path is None")

        in_path, out_path = get_tc_path(self.cases_path, self.tc)
        in_time = int(os.path.getmtime(in_path))
        out_time = int(os.path.getmtime(out_path))
        return in_time, out_time


class DiskCacheManager():

    def __init__(self, problem_name, tc):
        if not settings.DISK_CACHE_ENABLE:
            raise DiskCacheManagerException("Disk cache is not enabled")

        self.problem_name = problem_name
        self.tc = tc

    def insert(self, in_time, out_time, in_gzip, out_gzip):
        disk_cache.set(self.get_time_key(), (in_time, out_time))
        disk_cache.set(self.get_key(), (in_gzip, out_gzip))

    def get_content(self):
        d_gzip = disk_cache.get(self.get_key())
        if d_gzip is None:
            return None, None

        return d_gzip

    def get_time_content(self):
        d_time = disk_cache.get(self.get_time_key())
        if d_time is None:
            return None, None

        return d_time

    def get_key(self):
        return "CONTENT_{}-{}".format(self.problem_name, self.tc)

    def get_time_key(self):
        return "TIME_{}-{}".format(self.problem_name, self.tc)


class RedisCacheManagerException(Exception):
    pass


class DiskCacheManagerException(Exception):
    pass
