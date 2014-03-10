#!/usr/bin/python

__all__ = ["add_entries"]

config = {"json_output": False}

def add_entries(entries):
    if config['json_output']:
        import json
        for t in entries:
            for e in entries[t]:
                e["date"] = (str)(e["date"])
        print(json.dumps(entries))
    else: print(entries)

