#!/usr/bin/env python

from paranoia.types import *

class Socks4Request(Structure.simple([
        ('version', Byte, {'value': 0x4})
        ,('command', Byte)
        ,('port', Word, {'endianness': Word.BIG_ENDIAN})
        ,('ip', Dword, {'endianness': Dword.BIG_ENDIAN})
        ,('user_id', String)])):
    COMMAND_TCP_STREAM = 0x1
    COMMAND_TCP_BIND = 0x2

class Socks4Response(Structure.simple([
        ('null', Byte)
        ,('status', Byte)
        ,('port', Word, {'endianness': Word.BIG_ENDIAN})
        ,('ip', Dword, {'endianness': Dword.BIG_ENDIAN})])):
    STATUS_GRANTED = 0x5A
    STATUS_FAILED = 0x5B
    STATUS_IDENTD_NOT_RUNNING = 0x5C
    STATUS_IDENTD_FAILURE = 0x5D
