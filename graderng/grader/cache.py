import datetime

import redis

from django.conf import settings

from app import redis_connection_pool
from grader.constants import TESTCASE_PREFIX

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

        redis_conn.hmset(hashname, {
            in_key: in_gzip,
            out_key: out_gzip,
            mtime_key: float(mtime),
        })

        expire_time = datetime.timedelta(days=settings.REDIS_EXPIRE_TIME)
        redis_conn.expire(hashname, expire_time)

    @classmethod
    def get_mtime(cls, problem_name, tc):
        hashname = cls.get_hashname(problem_name, tc)
        mtime_key = cls.get_mtime_key()

        result = redis_conn.hget(hashname, mtime_key) or 0
        return float(result)

    @classmethod
    def get_content(cls, problem_name, tc):
        hashname = cls.get_hashname(problem_name, tc)
        in_key, out_key = cls.get_in_out_key(tc)

        return redis_conn.hmget(hashname, in_key, out_key)

    @staticmethod
    def get_hashname(problem_name, tc):
        return TESTCASE_PREFIX + "{}__{}".format(problem_name, tc)

    @staticmethod
    def get_in_out_key(tc):
        return ("in__{}".format(tc), "out__{}".format(tc))

    @staticmethod
    def get_mtime_key():
        return "mtime"
