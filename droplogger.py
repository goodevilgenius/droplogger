#!/usr/bin/python

import os
import os.path
import dateutil
import dateutil.parser as dp
import datetime
import re
import importlib
import json

first_line_re = re.compile("^@begin\s+([^-]+(?:\s-[0-9]{4})?)\s+-\s*(.*)")

def get_files(path, ext, recurse):
    r = []
    wext = ("." + ext) if (bool)(ext) else ""
    for f in os.listdir(path):
        full = os.path.join(path, f)
        if recurse and os.path.isdir(full):
            for subf in get_files(full, ext, True):
                r.append(os.path.join(f, subf))
        elif os.path.isfile(full) and f.endswith(wext):
            r.append(f)
    return r

def parse_item(item):
    yaml_bool = re.compile("^(y|Y|yes|Yes|YES|n|N|no|No|NO|true|True|TRUE|false|False|FALSE|on|On|ON|off|Off|OFF)$")
    yaml_true = re.compile("^(y|Y|yes|Yes|YES|true|True|TRUE|on|On|ON)$")
    yaml_null = re.compile("^(~|null|Null|NULL|none|None|NONE)")

    if isinstance(item, str):
        item = item.strip()
        if not (bool)(item):
            return None
        if yaml_null.match(item):
            return None
        if yaml_bool.match(item):
            item = bool(yaml_true.match(item))
            return item
        try:
            val = int(item)
            item = val
        except ValueError:
            try:
                val = float(item)
                item = val
            except ValueError:
                try:
                    val = dp.parse(item)
                    item = val
                except ValueError:
                    pass
    return item

def process_entry(entry, lists = None, list_separator = None):
    new = {}
    if lists is None:
        lists = read_config()['lists']
        if lists is None:
            lists = ["tags"]
    if list_separator is None:
        list_separator = read_config()['list_separator']
        if list_separator is None:
            list_separator = ","
    other_lines_re = re.compile("^@([^\s]+)\s*(.*)")
    
    lines = entry.splitlines()
    m = first_line_re.match(lines.pop(0))
    if not m: return False
    try:
        new["date"] = dp.parse(m.groups()[0])
    except ValueError:
        return False
    if new["date"].tzinfo is None:
        new["date"] = new["date"].replace(tzinfo = dateutil.tz.tzlocal())
    elif new["date"].tzinfo != dateutil.tz.tzlocal():
        new["date"] = new["date"].astimezone(dateutil.tz.tzlocal())
    k = "title"
    new[k] = m.groups()[1].strip().rsplit('@end',1)[0].strip()
    try:
        newline = lines.pop(0)
    except IndexError:
        newline = False
    while newline or newline == "":
        m = other_lines_re.match(newline)
        while not m and (newline or newline == ""):
            new[k] += "\n" + newline.strip().rsplit('@end',1)[0].strip()
            try:
                newline = lines.pop(0)
            except IndexError:
                newline = False
            if newline or newline == "": m = other_lines_re.match(newline)
        if not newline and newline != "": continue
        k = m.groups()[0]
        if k == "end": break
        new[k] = m.groups()[1].strip().rsplit('@end',1)[0].strip()
        try:
            newline = lines.pop(0)
        except IndexError:
            newline = False
    for k in new.keys():
        if k in lists:
            ar = []
            for i in new[k].split(list_separator):
                newi = parse_item(i)
                if newi is not None:
                    ar.append(newi)
            if len(ar) > 0:
                new[k] = ar
            else: del new[k]
        else:
            newk = parse_item(new[k])
            if newk is not None:
                new[k] = newk
            else:
                del new[k]
    return new

def read_files(path, files, ext, start, end):
    for f in files:
        these_entries = []
        name = f.rsplit('.'+ext, 1)[0] if (bool)(ext) else f
        full = os.path.join(path, f)
        with open(full) as f:
            line = f.readline()
            while line:
                if line.startswith('@begin'):
                    entry = line
                    if not entry.strip().endswith('@end'):
                        line = f.readline()
                        while line:
                            if line: entry += line
                            if line and line.strip().endswith('@end'): break
                            if not line: break
                            line = f.readline()
                    first_line = entry.splitlines()[0]
                    m = first_line_re.match(first_line)
                    if m:
                        date = m.groups()[0].strip()
                        try:
                            date = dp.parse(date)
                        except ValueError:
                            date = datetime.datetime.fromtimestamp(0)
                        if date.tzinfo is None:
                            date = date.replace(tzinfo = dateutil.tz.tzlocal())
                        if date and start <= date < end:
                            these_entries.append(process_entry(entry))
                line = f.readline()
        if len(these_entries) == 0: continue
        if not name in entries:
            entries[name] = these_entries
        else: entries[name].extend(these_entries)

    def sort_key(entry):
        return entry['date']

    for k in entries.keys():
        entries[k].sort(key=sort_key)

    return entries

def merge_dicts(a, b):
    if not isinstance(b, dict):
        return
    for k, v in b.iteritems():
        if k in a and isinstance(a[k], dict):
            merge_dicts(a[k], v)
        else:
            a[k] = v

def read_config():
    import appdirs

    config_dir = appdirs.user_data_dir('DropLogger','DanielRayJones')
    if not os.path.exists(config_dir): os.makedirs(config_dir)
    config_file = os.path.join(config_dir, 'config.json')
    if not os.path.exists(config_file) and not os.path.exists(os.path.join(config_dir, 'config.example.json')):
        ex_file = open(os.path.join(config_dir, 'config.example.json'), 'w')
        ex_config = {"__Instructions__": "Modify these settings, and save as config.json in " + config_dir
                    , "__lists__": "lists should contain a list of item types to be interpreted as lists"
                    , "path":os.path.join(os.path.expanduser('~'),'Dropbox','IFTTT','DropLogger')
                    , "ext": "txt"
                    , "recurse": True
                    , "lists": ["tags"]
                    , "list_separator": ","
                    , "outputs": ["stdout"]
                    , "output_config" : {
                        "stdout": {"json_output": False,"indent": True}
                        , "markdown_journal":
                        {"path": os.path.join(os.path.expanduser('~'),'Dropbox','Journal'),
                        "filename":"Journal_{}.md","main_header":"Journal for {}",
                        "short_date":"%Y-%m-%d","long_date":"%x",
                        "date_time":"%c"}
                        }}
        json.dump(ex_config, ex_file, indent=4)
        ex_file.close()

    config = {'output_config':{}}
    config['path'] = os.path.join(os.path.expanduser('~'),'Dropbox','IFTTT','DropLogger')
    config['ext'] = 'txt'
    config['recurse'] = True
    config['lists'] = ["tags"]
    config['list_separator'] = ","
    config['start'] = datetime.datetime.combine(datetime.date.today(),datetime.time.min.replace(tzinfo=dateutil.tz.tzlocal()))
    config['end']   = config['start'] + datetime.timedelta(days=1)
    config['outputs'] = ["stdout"]

    config['output_config']['stdout'] = {}
    config['output_config']['stdout']['json_output'] = False

    if os.path.exists(config_file):
        try:
            with open(config_file) as f:
                config_file_values = json.load(f)
        except ValueError as e:
            print("Couldn't read config file: %s" % config_file)
            print("Using default config values")
            print(e)
            config_file_values = {}
        merge_dicts(config, config_file_values)


    real_outputs = []
    for o in config['outputs']:
        try:
            real_outputs.append(importlib.import_module("outputs.%s" % o))
            if o in config['output_config']:
                for k in config['output_config'][o]:
                    real_outputs[len(real_outputs)-1].config[k] = config['output_config'][o][k]
        except ImportError:
            True
    config['outputs'] = real_outputs
	
    return config

if __name__ == "__main__":
    import sys,datetime

    config = read_config()

    if len(config['outputs']) == 0: sys.exit()
    entries = {}

    files = get_files(config['path'], config['ext'], config['recurse'])
    entries = read_files(config['path'], files, config['ext'], config['start'], config['end'])

    for o in config['outputs']:
        o.add_entries(entries)
