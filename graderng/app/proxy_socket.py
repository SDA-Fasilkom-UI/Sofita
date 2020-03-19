import socks

from urllib.parse import urlparse

from django.conf import settings


class ProxySocket():

    @staticmethod
    def socket():
        s = socks.socksocket()
        if settings.HTTP_PROXY:
            o = urlparse(settings.HTTP_PROXY)
            location, port = o.netloc.split(":")
            s.set_proxy(socks.HTTP, location, int(port))

        return s
