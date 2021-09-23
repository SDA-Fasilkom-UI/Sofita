import datetime

import redis

from django.conf import settings

from app import disk_cache, redis_connection_pool

redis_conn = redis.Redis(connection_pool=redis_connection_pool)


class TestcaseCache():
    """
    responsible to set/get testcase cache
    """

    @classmethod
    def insert(cls, problem_name, tc, in_gzip, out_gzip, mtime):
        hashname = cls.get_hashname(problem_name, tc)
        in_key, out_key = cls.get_in_out_key(tc)
        mtime_key = cls.get_mtime_key()

        mtime = int(mtime)
        redis_conn.hmset(hashname, {
            in_key: in_gzip,
            out_key: out_gzip,
            mtime_key: mtime,
        })

        expire_time = datetime.timedelta(days=settings.REDIS_EXPIRE_TIME)
        redis_conn.expire(hashname, expire_time)

        if settings.DISK_CACHE_ENABLE:
            cls._insert_to_disk(problem_name, tc, in_gzip, out_gzip, mtime)

    @classmethod
    def get_mtime(cls, problem_name, tc):
        hashname = cls.get_hashname(problem_name, tc)
        mtime_key = cls.get_mtime_key()

        r_mtime = redis_conn.hget(hashname, mtime_key) or -1
        return int(r_mtime)

    @classmethod
    def get_content(cls, problem_name, tc):
        hashname = cls.get_hashname(problem_name, tc)
        in_key, out_key = cls.get_in_out_key(tc)

        if settings.DISK_CACHE_ENABLE:
            d_mtime = cls._get_disk_mtime(problem_name, tc)
            r_mtime = cls.get_mtime(problem_name, tc)
            if d_mtime >= r_mtime:
                d_gzip = disk_cache.get(cls.get_hashname(problem_name, tc))
                if d_gzip is not None:
                    return d_gzip

            # update stale disk cache
            in_gzip, out_gzip = redis_conn.hmget(hashname, in_key, out_key)
            cls._insert_to_disk(problem_name, tc, in_gzip, out_gzip, r_mtime)

            return in_gzip, out_gzip

        return redis_conn.hmget(hashname, in_key, out_key)

    @staticmethod
    def get_hashname(problem_name, tc):
        return "TESTCASE_" + "{}__{}".format(problem_name, tc)

    @staticmethod
    def get_in_out_key(tc):
        return ("in__{}".format(tc), "out__{}".format(tc))

    @staticmethod
    def get_mtime_key():
        return "mtime"

    @classmethod
    def _insert_to_disk(cls, problem_name, tc, in_gzip, out_gzip, mtime):
        hashname = cls.get_hashname(problem_name, tc)
        d_mtime_key = cls._get_disk_mtime_key(problem_name, tc)

        expire_seconds = datetime.timedelta(
            days=settings.REDIS_EXPIRE_TIME).total_seconds()

        disk_cache.set(d_mtime_key, mtime, expire=expire_seconds)
        disk_cache.set(hashname, (in_gzip, out_gzip), expire=expire_seconds)

    @classmethod
    def _get_disk_mtime(cls, problem_name, tc):
        d_mtime_key = cls._get_disk_mtime_key(problem_name, tc)
        d_mtime = disk_cache.get(d_mtime_key) or -1
        return int(d_mtime)

    @classmethod
    def _get_disk_mtime_key(cls, problem_name, tc):
        return cls.get_hashname(problem_name, tc) + "_" + cls.get_mtime_key()
