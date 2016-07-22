#!/usr/bin/env python

import socket

from martinellis.address import V4Address, V6Address

class ClientError(Exception):
    pass

class Client(socket.socket):
    SOCKET_FAMILY = socket.AF_INET
    SOCKET_TYPE = socket.SOCK_STREAM
    ADDRESS = None
    PORT = None

    def __init__(self, **kwargs):
        self.socket_family = kwargs.setdefault('socket_family', self.SOCKET_FAMILY)
        self.socket_type = kwargs.setdefault('socket_type', self.SOCKET_TYPE)
        self.address = kwargs.setdefault('address', self.ADDRESS)
        self.port = kwargs.setdefault('port', self.PORT)

        if not self.socket_family in (socket.AF_INET, socket.AF_INET6):
            raise ClientError('family must be AF_INET or AF_INET6')

        if not self.socket_type in (socket.SOCK_STREAM, socket.SOCK_DGRAM):
            raise ClientError('type must be SOCK_STREAM or SOCK_DGRAM')

        if self.address is None:
            raise ClientError('no client address provided')

        try:
            if self.socket_family == socket.AF_INET:
                address_object = V4Address.from_string(self.address)
            elif self.socket_family == socket.AF_INET6:
                address_object = V6Address.from_string(self.address)
            else:
                raise
        except:
            raise ClientError('invalid address object given')

        if self.port is None:
            raise ClientError('no client port given')

        if not isinstance(self.port, (int, long)):
            raise ClientError('port must be a number')

        if not 0 <= self.port <= 65535:
            raise ClientError('bad port value given')
        
        socket.socket.__init__(self, self.socket_family, self.socket_type)
