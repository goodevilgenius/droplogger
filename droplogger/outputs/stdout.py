#!/usr/bin/python

import json
from ..utils.misc import serialize_json
__all__ = ["add_entries"]
config = {"__Instructions__":"if json_output is true, will be output in JSON format. With indent set true, it will be pretty-printed","json_output": False, "indent": True}

def add_entries(entries):
    if config['json_output']:
        import copy
        c = copy.deepcopy(entries)
        if config['indent']: print(json.dumps(c, indent=4, default=serialize_json))
        else: print(json.dumps(c, default=serialize_json))
    else:
        import os
        for cat,ents in entries.items():
            print(cat.replace(os.sep,'.'))
            print("=======")
            for i in ents:
                for k,v in i.items():
                    print("%s: %s" % (k,v))
                print('')
            print('')

