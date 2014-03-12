#!/usr/bin/python

import os.path

__all__ = ["add_entries"]

config = {"path": os.path.join(os.path.expanduser('~'),'Dropbox/Journal'),
          "filename":"Journal_{}.md","main_header":"Journal for {}",
          "short_date":"%Y-%m-%d","long_date":"%x",
          "date_time":"%c"}

def add_entries(entries):
    if not entries: return
    
    import os
    if not os.path.isdir(config["path"]): os.mkdir(config["path"])

    date = entries[entries.keys()[0]][0]["date"]
    f = os.path.join(config["path"], config["filename"].format(date.strftime(config["short_date"])))
    fo = open(f, 'w')

    fo.write("# " + config["main_header"].format(date.strftime(config["long_date"])))
    fo.write("\n\n")

    if "diary" in entries:
        for e in entries["diary"]:
            fo.write(e["text"])
            fo.write("\n\n")

    for t in entries:
        if t == "diary": continue
        fo.write('## ' + t)
        fo.write("\n\n")
        for e in entries[t]:
            fo.write('* ')
            fo.write(e["date"].strftime(config["date_time"]))
            fo.write(" - ")
            if "url" in e and e["url"] is not None: fo.write('[')
            fo.write(e["title"])
            if "url" in e and e["url"] is not None: fo.write('](' + e["url"] + ')')
            fo.write("\n")
        fo.write("\n")
