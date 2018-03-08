#!/usr/bin/python

import json
__all__ = ["add_entries"]
config = {"__Instructions__":"if json_output is true, will be output in JSON format. With indent set true, it will be pretty-printed","json_output": False, "indent": True}

class MyJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            e = json.JSONEncoder()
            e.encode(obj)
        except TypeError:
            return (str)(obj)
        return json.JSONEncoder.default(self, obj)

def add_entries(entries):
    if config['json_output']:
        import copy
        c = copy.deepcopy(entries)
        if config['indent']: print(json.dumps(c, indent=4, cls=MyJSONEncoder))
        else: print(json.dumps(c, cls=MyJSONEncoder))
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

