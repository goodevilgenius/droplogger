#!/usr/bin/python

__all__ = ["add_entries"]

config = {"json_output": False, "indent": True}

def add_entries(entries):
    if config['json_output']:
        import json, copy
        c = copy.deepcopy(entries)
        for t in c:
            for e in c[t]:
                e["date"] = (str)(e["date"])
        if config['indent']: print(json.dumps(c, indent=4))
        else: print(json.dumps(c))
    else:
        import os
        for cat,ents in entries.iteritems():
            print cat.replace(os.sep,'.')
            print "======="
            for i in ents:
                for k,v in i.iteritems():
                    print("%s: %s" % (k,v))
                print('')
            print('')

