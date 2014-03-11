#!/usr/bin/python

__all__ = ["add_entries"]

config = {"db": "droplog","host": "localhost", "port": 27017}

def add_entries(entries):
    import pymongo
    try:
        cl = pymongo.MongoClient(config['host'], config['port'])
    except AttributeError:
        cl = pymongo.Connection(config['host'], config['port'])
    db = cl[config['db']]

    for t in entries:
        for e in entries[t]:
            thisone = db[t].find_one({"date":e["date"],"title":e["title"]})
            if thisone is not None: db[t].update(thisone, e)
            else: db[t].insert(e)
