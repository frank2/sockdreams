#!/usr/bin/env python

import os
import sys

from sockdreams.clients import socks5

def main(*args):
    client = socks5.Socks5Client(address='127.0.0.1', port=8080)
    client.connect(('slashdot.org', 80))
    client.send('GET / HTTP/1.1\r\n\r\n')
    print client.recv(1024)

if __name__ == '__main__':
    main(*sys.argv[:1])
