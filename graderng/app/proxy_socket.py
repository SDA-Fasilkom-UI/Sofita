import socket

from urllib.parse import urlparse

from django.conf import settings


class ProxySocket():
    """
    Establish a socket connection through an HTTP proxy.
    Author: Fredrik Østrem <frx.apps@gmail.com>
    License:
        This code can be used, modified and distributed freely, as long as it is this note containing the original
        author, the source and this license, is put along with the source code.

    Copied and edited from: https://gist.github.com/frxstrem/4487802
    """

    @staticmethod
    def _valid_address(addr):
        """ Verify that an IP/port tuple is valid """
        return isinstance(addr, (list, tuple)) and len(addr) == 2 and isinstance(addr[0], str) and isinstance(addr[1], int)

    @classmethod
    def connect(cls, address):
        """
        Establish a socket connection through an HTTP proxy.

        Arguments:
        address (required)     = The address of the target
        proxy (def: None)      = The address of the proxy server
        headers (def: {})      = A set of headers that will be sent to the proxy

        Returns:
        A 3-tuple of the format:
            (socket, status_code, headers)
        Where `socket' is the socket object, `status_code` is the HTTP status code that the server
        returned and `headers` is a dict of headers that the server returned.
        """

        if not cls._valid_address(address):
            raise ValueError('Invalid target address')

        proxy = None
        if settings.HTTP_PROXY:
            o = urlparse(settings.HTTP_PROXY)
            location, port = o.netloc.split(":")
            proxy = (location, int(port))

        if proxy is None:
            s = socket.socket()
            s.connect(address)
            return s, 0, {}

        if not cls._valid_address(proxy):
            raise ValueError('Invalid proxy address')

        headers = {
            'host': address[0]
        }

        s = socket.socket()
        s.connect(proxy)
        fp = s.makefile('rw')  # r+ doesn't work, so changed it to rw

        fp.write('CONNECT %s:%d HTTP/1.0\r\n' % address)
        fp.write('\r\n'.join('%s: %s' % (k, v)
                             for (k, v) in headers.items()) + '\r\n\r\n')
        fp.flush()

        statusline = fp.readline().rstrip('\r\n')

        if statusline.count(' ') < 2:
            fp.close()
            s.close()
            raise IOError('Bad response')

        version, status, statusmsg = statusline.split(' ', 2)
        if not version in ('HTTP/1.0', 'HTTP/1.1'):
            fp.close()
            s.close()
            raise IOError('Unsupported HTTP version')

        try:
            status = int(status)
        except ValueError:
            fp.close()
            s.close()
            raise IOError('Bad response')

        response_headers = {}

        while True:
            tl = ''
            l = fp.readline().rstrip('\r\n')
            if l == '':
                break
            if not ':' in l:
                continue
            k, v = l.split(':', 1)
            response_headers[k.strip().lower()] = v.strip()

        fp.close()
        return (s, status, response_headers)
