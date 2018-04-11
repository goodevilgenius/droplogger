#!/usr/bin/env python

import sys, json

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

def merge_dicts(a, b):
    if not isinstance(b, dict):
        return
    for k, v in b.items():
        if k in a and isinstance(a[k], dict):
            merge_dicts(a[k], v)
        else:
            a[k] = v

def serialize_json(obj):
    return get_string(obj)

def json_dumps(obj):
    return json.dumps(obj, default=serialize_json)
