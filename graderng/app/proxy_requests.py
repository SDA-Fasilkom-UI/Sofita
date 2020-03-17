import requests

from django.conf import settings


class ProxyRequests():

    proxies = None
    if settings.HTTP_PROXY:
        proxies = {
            "http": settings.HTTP_PROXY,
            "https": settings.HTTP_PROXY
        }

    @classmethod
    def get(cls, *args, **kwargs):
        kwargs["proxies"] = cls.proxies
        return requests.get(*args, **kwargs)

    @classmethod
    def post(cls, *args, **kwargs):
        kwargs["proxies"] = cls.proxies
        return requests.post(*args, **kwargs)
