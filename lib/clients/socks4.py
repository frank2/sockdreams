#!/usr/bin/env python

import socket

from martinellis.address import V4Address, AddressError

from sockdreams.packets import socks4
from sockdreams.clients import client

class Socks4ClientError(Exception):
    pass

class Socks4Client(client.Client):
    USERNAME = None
    REQUEST_PACKET = socks4.Socks4Request # so we can subclass Socks4a

    def __init__(self, **kwargs):
        self.username = kwargs.setdefault('username', self.USERNAME)
        self.request_packet = kwargs.setdefault('request_packet', self.REQUEST_PACKET)
        self.command = None

        client.Client.__init__(self, **kwargs)

    def build_request(self, target_address, port):
        if not self.socket_family == socket.AF_INET:
            raise Socks4ClientError('socks4 only supports ipv4')

        if not self.socket_type == socket.SOCK_STREAM:
            raise Socks4ClientError('socks4 only supports tcp')

        if not self.command in (socks4.Socks4Request.COMMAND_TCP_STREAM
                                ,socks4.Socks4Request.COMMAND_TCP_BIND):
            raise Socks4ClientError('command must be Socks4Request.COMMAND_TCP_STREAM or Socks4Request.COMMAND_TCP_BIND')
        
        target_address = V4Address.from_string(target_address)

        connection_request = self.request_packet()
        connection_request.command.set_value(self.command)
        connection_request.port.set_value(port)
        connection_request.ip.set_value(int(target_address))

        if not self.username is None:
            connection_request.username.set_value(self.username)

        return connection_request
    
    def establish(self, target_address, port, sock_obj=None):
        if sock_obj is None:
            sock_obj = self

        self.command = socks4.Socks4Request.COMMAND_TCP_STREAM
        request_packet = self.build_request(target_address, port)

        sock_obj.send(request_packet.read_memory())
        response_data = sock_obj.recv(1024)

        if not len(response_data):
            raise Socks4ClientError('got no response from the server')
        
        response_packet = socks4.Socks4Response(string_data=response_data)

        if not int(response_packet.status) == socks4.Socks4Response.STATUS_GRANTED:
            raise Socks4ClientError('client negotiation failed')
