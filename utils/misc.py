#!/usr/bin/env python

import sys

def is_string(item):
    if sys.version_info >= (3,0,0):
        return isinstance(item, str)
    else:
        return isinstance(item, unicode) or isinstance(item, str)

def get_string(item):
    if sys.version_info >= (3,0,0):
        return str(item)
    else:
        return unicode(item)

