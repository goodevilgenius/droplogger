#!/usr/bin/python

import os.path,re

__all__ = ["add_entries"]

config = {"path": os.path.join(os.path.expanduser('~'),'Dropbox/Journal'),
          "filename":"Journal_{}.md","main_header":"Journal for {}",
          "short_date":"%Y-%m-%d","long_date":"%x",
          "date_time":"%c"}

space_re = re.compile('\s+')

def add_entries_helper(entries, key, level, fo):
    if not entries: return
    if not key: return
    if not level: return

    subs = find_sub_keys(entries, key)
    if not key in entries and len(subs) == 0: return

    fo.write(('#'*level) + ' ' + key)
    fo.write("\n\n")
    if key in entries:
        for e in entries[key]:
            fo.write('* ')
            fo.write(e["date"].strftime(config["date_time"]))
            fo.write(" - ")
            if "url" in e and e["url"] is not None: fo.write('[')
            fo.write(space_re.sub(' ', e["title"]))
            if "url" in e and e["url"] is not None: fo.write('](' + e["url"] + ')')
            fo.write("\n")
        fo.write("\n")
        del entries[key]

    for sk in subs:
        add_entries_helper(entries, sk, level+1, fo)

def find_sub_keys(entries, key):
    if not entries: return
    if not key: return

    r = []
    for k in entries:
        if k.startswith(key + "/"): r.append(k)
    return r

def add_entries(entries):
    if not entries: return
    
    import os, copy
    if not os.path.isdir(config["path"]): os.mkdir(config["path"])

    c = copy.deepcopy(entries)    

    date = c[c.keys()[0]][0]["date"]
    f = os.path.join(config["path"], config["filename"].format(date.strftime(config["short_date"])))
    fo = open(f, 'w')

    fo.write("# " + config["main_header"].format(date.strftime(config["long_date"])))
    fo.write("\n\n")

    if "diary" in c:
        for e in c["diary"]:
            fo.write(e["text"])
            fo.write("\n\n")
        del c["diary"]
    
    for k in find_sub_keys(c, "diary"):
        for e in c[k]:
            fo.write(e["text"])
            fo.write("\n\n")
        del c[k]

    for t in c.keys():
        if not t in c: continue
        if t.count('/') > 0:
            i = t.index('/')
            add_entries_helper(c, t[:i], 2, fo)
        add_entries_helper(c, t, 2, fo)
    
    fo.close()
