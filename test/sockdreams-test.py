#!/usr/bin/env python

import os
import sys

from sockdreams.clients import socks5, http

def main(*args):
    client = http.HTTPClient(address='127.0.0.1', port=3128)
    client.connect(('cnn.com', 80))
    client.send('GET / HTTP/1.1\r\nHost: www.cnn.com\r\n\r\n')
    print client.recv(1024)

if __name__ == '__main__':
    main(*sys.argv[:1])
