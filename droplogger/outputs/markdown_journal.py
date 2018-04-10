#!/usr/bin/python

import os, os.path, re

__all__ = ["add_entries"]

config = {"__Instructions__":"In filename and main_header, {} is replaced with the log title",
          "path": os.path.join(os.path.expanduser('~'),'Dropbox','Journal'),
          "filename":"Journal_{}.md","main_header":"Journal for {}",
          "short_date":"%Y-%m-%d","long_date":"%x",
          "date_time":"%c"}

space_re = re.compile('\s+')

def add_entries_helper(entries_to_send, entries, key):
    if not entries: return
    if not key: return

    if not key.replace(os.sep,'.') in entries_to_send: entries_to_send[key.replace(os.sep,'.')] = {}

    subs = find_sub_keys(entries, key)
    if len(subs) > 0:
        entries_to_send[key.replace(os.sep,'.')]["subs"] = {}
        for sk in subs:
            add_entries_helper(entries_to_send[key.replace(os.sep,'.')]["subs"], entries, sk)

    if key in entries:
        entries_to_send[key.replace(os.sep,'.')]["entries"] = entries[key]
        del entries[key]
        for e in entries_to_send[key.replace(os.sep,'.')]["entries"]:
            e["title"] = space_re.sub(' ', e["title"])
            if "tags" in e: e["tags"] = map(unicode, e["tags"])
            for e_key in e.keys():
                if e_key == "note" or e_key == "notes":
                    val = re.sub('^  ', '', re.sub('^', '    ', e[e_key], 0, re.M))
                    while re.search('\n  \n', val):
                        val = re.sub('\n  \n', '\n\n', val)
                    e[e_key] = val

    if not entries_to_send[key.replace(os.sep,'.')]: del entries_to_send[key.replace(os.sep,'.')]

def find_sub_keys(entries, key):
    if not entries: return []
    if not key: return []

    r = []
    for k in entries:
        if k.startswith(key + os.sep): r.append(k)
    return r

def get_diary(entries, key, header = '', use_title = False):
    diary = ""
    if key in entries:
        for e in entries[key]:
            if use_title: diary = diary + '### ' + e['title'] + "\n\n"
            diary = diary + e["text"]
            diary = diary + "\n\n"
        del entries[key]

    for k in find_sub_keys(entries, key):
        for e in entries[k]:
            if use_title: diary = diary + '### ' + e['title'] + "\n\n"
            diary = diary + e["text"]
            diary = diary + "\n\n"
        del entries[k]
    if bool(header) and bool(diary):
        diary = '## ' + header + '\n\n' + diary
    return diary

def add_entries(entries):
    if not entries: return
    
    import os, copy, codecs, jinja2
    if not os.path.isdir(config["path"]): os.mkdir(config["path"])

    c = copy.deepcopy(entries)
    entries_to_send = {}

    date = c[list(c.keys())[0]][0]["date"]

    diary = get_diary(c, "diary")
    diary = diary + get_diary(c, "dreams", "Dreams", True)

    f = os.path.join(config["path"], config["filename"].format(date.strftime(config["short_date"])))
    fo = codecs.open(f, 'w', encoding='utf-8')

    title = config["main_header"].format(date.strftime(config["long_date"]))

    for key in list(c.keys()):
        if not key in c: continue
        if key.count(os.sep) > 0:
            i = key.index(os.sep)
            add_entries_helper(entries_to_send, c, key[:i])
        else:
            add_entries_helper(entries_to_send, c, key)

    templates_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates')
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(templates_path))
    temp = env.get_template("markdown.tpl")
    out = temp.render(title=title, diary=diary, config=config, entries=entries_to_send)

    fo.write(out)
    fo.close()
