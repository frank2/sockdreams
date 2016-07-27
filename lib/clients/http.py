#!/usr/bin/env python

import socket
import re

from sockdreams.clients import client

class HTTPClientError(Exception):
    pass

class HTTPClient(client.Client):
    def establish(self, address, port, sock_obj=None):
        if sock_obj is None:
            sock_obj = self

        connection_string = ('CONNECT %s:%d HTTP/1.1\r\n'
                             'Host: %s:%d\r\n\r\n') % (address, port, address, port)

        sock_obj.send(connection_string)
        data = sock_obj.recv(1024)
        match = re.match('HTTP/\\d.\\d (\\d+)', data)

        if not match:
            raise HTTPClientError('server does not appear to be an http server')

        status = match.group(1)

        if not status == '200':
            raise HTTPClientError('proxy connection could not be established')
