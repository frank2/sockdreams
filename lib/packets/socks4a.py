#!/usr/bin/env python

from paranoia.types import *
from paranoia.base.declaration import Declaration
from . import socks4

class Socks4aRequest(socks4.Socks4Request):
    FIELDS = socks4.Socks4Request.FIELDS[:] + [('domain'
                                                ,Declaration(base_class=String))]
    
class Socks4aResponse(socks4.Socks4Response):
    pass
    
