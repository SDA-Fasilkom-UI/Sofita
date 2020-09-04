from urllib.parse import urlparse

from django.conf import settings


class ProxySocket():

    @staticmethod
    def get_original_socks():
        """
        Hacky way to solve connection reset error on gevent,
        not sure why it is happened. This function will patch
        the base class of socks to original socket.
        https://stackoverflow.com/questions/8544983/
        """

        from test import support
        socks = support.import_fresh_module("socks")
        socket = support.import_fresh_module("socket")

        socks._orgsocket = socks._orig_socket = socket.socket
        socks._BaseSocket = type(
            "_BaseSocket", (socket.socket,), dict(socks._BaseSocket.__dict__))
        socks.socksocket = type(
            "socksocket", (socks._BaseSocket,), dict(socks.socksocket.__dict__))
        return socks

    @classmethod
    def socket(cls):
        socks = cls.get_original_socks()
        s = socks.socksocket()
        if settings.HTTP_PROXY:
            o = urlparse(settings.HTTP_PROXY)
            location, port = o.netloc.split(":")
            s.set_proxy(socks.HTTP, location, int(port))

        return s
