#!/usr/bin/python

__all__ = ["add_entries"]

config = {"db": "droplog","host": "localhost", "port": 27017}

def add_entries(entries):
    import pymongo, re, os
    try:
        cl = pymongo.MongoClient(config['host'], config['port'])
    except AttributeError:
        cl = pymongo.Connection(config['host'], config['port'])
    db = cl[config['db']]

    for t in entries:
        name = re.sub('\.+','.',t.replace(os.sep,'.'))
        for e in entries[t]:
            thisone = db[name].find_one({"date":e["date"],"title":e["title"]})
            if thisone is not None: db[name].update(thisone, e)
            else: db[name].insert(e)
