#!/usr/bin/env python

import socket

from martinellis.address import V4Address, AddressError

from sockdreams.packets import socks4a
from sockdreams.clients import socks4

class Socks4aClientError(Exception):
    pass

class Socks4aClient(socks4.Socks4Client):
    REQUEST_PACKET = socks4a.Socks4aRequest

    def build_request(self, target_address, port):
        request = super(self, Socks4aClient).build_request('0.0.0.1', port)

        request.domain.set_value(target_address)

        return request
