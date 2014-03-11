#!/usr/bin/python

__all__ = ["add_entries"]

config = {"json_output": False}

def add_entries(entries):
    if config['json_output']:
        import json, copy
        c = copy.deepcopy(entries)
        for t in c:
            for e in c[t]:
                e["date"] = (str)(e["date"])
        print(json.dumps(c))
    else: print(entries)

