#!/usr/bin/env python

import socket

from martinellis.address import V4Address, V6Address, AddressError

from sockdreams.packets import socks5
from sockdreams.clients import client

class Socks5ClientError(Exception):
    pass

class Socks5Client(client.Client):
    DOMAIN = None
    USERNAME = None
    PASSWORD = None

    def __init__(self, **kwargs):
        self.domain = kwargs.setdefault('domain', self.DOMAIN)
        self.username = kwargs.setdefault('username', self.USERNAME)
        self.password = kwargs.setdefault('password', self.PASSWORD)

        client.Client.__init__(self, **kwargs)

    def establish(self, target_address, port, sock_obj=None):
        if sock_obj is None:
            sock_obj = self
            
        try:
            if self.socket_family == socket.AF_INET:
                target_address = V4Address.from_string(target_address)
            elif self.socket_family == socket.AF_INET6:
                target_address = V6Address.from_string(target_address)

            target_domain = None
        except AddressError:
            target_domain = target_address
            target_address = None

        hello_packet = socks5.Socks5HelloRequest()
        auth_methods = [socks5.Socks5HelloRequest.AUTH_NONE]

        if not self.username is None:
            auth_methods.append(socks5.Socks5HelloRequest.AUTH_USERNAME_PASSWORD)
        
        hello_packet.auth_method_size.set_value(len(auth_methods))

        for i in xrange(len(auth_methods)):
            hello_packet.auth_methods[i].set_value(auth_methods[i])

        sock_obj.send(hello_packet.read_memory())
        response_data = sock_obj.recv(1024)
        response_packet = socks5.Socks5HelloResponse(string_data=response_data)

        if int(response_packet.authentication) == socks5.Socks5HelloResponse.AUTH_INVALID:
            raise Socks5ClientError('supplied authentication methods are invalid')
            
        elif not int(response_packet.authentication) in auth_methods:
            raise Socks5ClientError('authentication method not requested')
        
        if int(response_packet.authentication) == socks5.Socks5HelloRequest.AUTH_USERNAME_PASSWORD:
            self.authenticate(sock_obj)

        # otherwise it's no authentication
        connection_packet = socks5.Socks5ConnectionRequest()

        if self.socket_type == socket.SOCK_STREAM:
            connection_packet.status.set_value(socks5.Socks5ConnectionRequest.COMMAND_TCP_STREAM)
        elif self.socket_type == socket.SOCK_DGRAM:
            connection_packet.status.set_value(socks5.Socks5ConnectionRequest.COMMAND_UDP_BIND)

        if not target_address is None and isinstance(target_address, V4Address):
            connection_packet.destination.type.set_value(socks5.Socks5Destination.TYPE_IPV4)
            connection_packet.destination.address.type_instance().set_value(int(target_address))
        elif not target_address is None and isinstance(target_address, V6Address):
            connection_packet.destination.type.set_value(socks5.Socks5Destination.TYPE_IPV6)
            connection_packet.destination.address.type_instance().set_value(int(target_address))
        elif not target_domain is None:
            connection_packet.destination.type.set_value(socks5.Socks5Destination.TYPE_DOMAIN)
            connection_packet.destination.address.type_instance().set_string_value(target_domain)

        connection_packet.port.set_value(port)

        sock_obj.send(connection_packet.read_memory())
        response_data = sock_obj.recv(1024)
        response_packet = socks5.Socks5ConnectionResponse(string_data=response_data)

        if not int(response_packet.status) == 0:
            raise Socks5ClientError('server responded with an error')

    def authenticate(self, sock_obj=None):
        if sock_obj is None:
            sock_obj = self
            
        raise Socks5ClientError('username/password authentication not yet implemented')
