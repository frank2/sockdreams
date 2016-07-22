#!/usr/bin/env python

from paranoia.base.size_hint import SizeHint
from paranoia.base.declaration import Declaration
from paranoia.meta.list import List
from paranoia.types import *

class Socks5PacketError(Exception):
    pass

class Socks5String(Structure.simple([
        ('size', SizeHint, {'bitspan': 8
                            ,'argument': 'elements'
                            ,'target_declaration': 'string'})
        ,('string', String, {'bind': True
                             ,'zero_terminated': False})])):
    def set_string_value(self, string):
        if len(string) >= 256:
            raise Socks5PacketError('string exceeds 255 bytes')

        self.size.set_value(len(string))
        self.string.set_value(string)

# the destination isn't really a union because the size of the object is dependent
# on its type
class Socks5Destination(List):
    BASE_DECLARATIONS = [[Declaration(base_class=Dword)]
                         ,[Declaration(base_class=Socks5String)]
                         ,[Declaration(base_class=Oword)]]
    TYPE_IPV4 = 0x1
    TYPE_DOMAIN = 0x3
    TYPE_IPV6 = 0x4
    TYPE = TYPE_IPV4

    def __init__(self, **kwargs):
        self.type = kwargs.setdefault('type', self.TYPE)
        self.base_declarations = map(lambda x: map(Declaration.copy, x), kwargs.setdefault('base_declarations', self.BASE_DECLARATIONS))
        self.copy_declarations = kwargs.setdefault('copy_declarations', self.COPY_DECLARATIONS)
       
        if not self.type in [self.TYPE_IPV4, self.TYPE_DOMAIN, self.TYPE_IPV6]:
            raise Socks5Error('destination type must be TYPE_IPV4, TYPE_DOMAIN or TYPE_IPV6')

        self.instance_map = dict()
        self.set_declarations()

        kwargs['declarations'] = self.declarations
        List.__init__(self, **kwargs)

        self.recalculate()

    def set_declarations(self):
        if self.type == self.TYPE_IPV4:
            new_decls = self.base_declarations[0]
        elif self.type == self.TYPE_DOMAIN:
            new_decls = self.base_declarations[1]
        elif self.type == self.TYPE_IPV6:
            new_decls = self.base_declarations[2]
        else:
            raise Socks5PacketError('invalid type')

        decl_hash = hash(new_decls[0])

        if self.instance_map.has_key(decl_hash):
            self.instance_map[decl_hash].invalidated = True
            del self.instance_map[decl_hash]

        self.declarations = new_decls

        self.map_declarations()

    def set_type(self, type_val):
        if not type_val in [self.TYPE_IPV4, self.TYPE_DOMAIN, self.TYPE_IPV6]:
            raise Socks5Error('destination type must be TYPE_IPV4, TYPE_DOMAIN or TYPE_IPV6')

        if type_val == self.type:
            return
        
        self.type = type_val
        self.set_declarations()
        self.recalculate()

    def type_instance(self):
        return self[0]

    @classmethod
    def static_bitspan(cls, **kwargs):
        dest_type = kwargs.setdefault('type', cls.TYPE)

        if dest_type == cls.TYPE_IPV4:
            kwargs['declarations'] = cls.BASE_DECLARATIONS[0]
        elif dest_type == cls.TYPE_DOMAIN:
            kwargs['declarations'] = cls.BASE_DECLARATIONS[1]
        elif dest_type == cls.TYPE_IPV6:
            kwargs['declarations'] = cls.BASE_DECLARATIONS[2]
        else:
            kwargs['declarations'] = list()

        return super(Socks5Destination, cls).static_bitspan(**kwargs)

class Socks5ConnectionAddress(Structure.simple([
        ('type', SizeHint, {'bitspan': 8
                             ,'argument': 'type'
                             ,'target_declaration': 'address'})
        ,('address', Socks5Destination)])):
    pass

class Socks5HelloRequest(Structure.simple([
        ('version', Byte, {'value': 0x5})
        ,('auth_method_size', SizeHint, {'bitspan': 8
                                         ,'argument': 'elements'
                                         ,'target_declaration': 'auth_methods'})
        ,('auth_methods', ByteArray)])):
    AUTH_NONE = 0x0
    AUTH_GSSAPI = 0x1
    AUTH_USERNAME_PASSWORD = 0x2

class Socks5HelloResponse(Structure.simple([
        ('version', Byte)
        ,('authentication', Byte)])):
    AUTH_INVALID = 0xFF

class Socks5UserPassAuthRequest(Structure.simple([
        ('version', Byte)
        ,('username', Socks5String)
        ,('password', Socks5String)])):
    pass

class Socks5UserPassAuthResponse(Structure.simple([
        ('version', Byte)
        ,('status', Byte)])):
    STATUS_SUCCESS = 0

class Socks5ConnectionRequest(Structure.simple([
        ('version', Byte, {'value': 0x5})
        ,('status', Byte)
        ,('reserved', Byte, {'value': 0x0})
        ,('destination', Socks5ConnectionAddress)
        ,('port', Word, {'endianness': Word.BIG_ENDIAN})])):
    COMMAND_TCP_STREAM = 0x1
    COMMAND_TCP_BIND = 0x2
    COMMAND_UDP_BIND = 0x3

class Socks5ConnectionResponse(Socks5ConnectionRequest):
    pass
