#!/usr/bin/python

import os
import os.path
import dateutil
import dateutil.parser as dp
import datetime
import re

first_line_re = re.compile("^@begin\s+([^-]+)\s*-\s*(.+)")

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

def process_entry(entry):
    new = {}
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
    k = "title"
    new[k] = m.groups()[1].strip().rsplit('@end',1)[0].strip()
    try:
        newline = lines.pop(0)
    except IndexError:
        newline = False
    while newline:
        m = other_lines_re.match(newline)
        while not m and newline:
            new[k] += "\n" + newline.strip().rsplit('@end',1)[0].strip()
            try:
                newline = lines.pop(0)
            except IndexError:
                newline = False
            if newline: m = other_lines_re.match(newline)
        if not newline: continue
        k = m.groups()[0]
        if k == "end": break
        new[k] = m.groups()[1].strip().rsplit('@end',1)[0].strip()
        try:
            newline = lines.pop(0)
        except IndexError:
            newline = False
    for k in new.keys():
        if isinstance(new[k], str): new[k] = new[k].strip()
        if not (bool)(new[k]): del new[k]
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
                    line = f.readline()
                    if not entry.strip().endswith('@end'):
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
                            date = False
                        if date.tzinfo is None:
                            date = date.replace(tzinfo = dateutil.tz.tzlocal())
                        if date and start <= date < end:
                            these_entries.append(process_entry(entry))
                line = f.readline()
        if len(these_entries) == 0: continue
        if not name in entries:
            entries[name] = these_entries
        else: entries[name].extend(these_entries)
    return entries

def read_config():
    import appdirs

    config_dir = appdirs.user_data_dir('DropLogger','DanielRayJones')
    if not os.path.exists(config_dir): os.mkdir(config_dir)
    config_file = os.path.join(config_dir, 'config.json')
    if not os.path.exists(config_file) and not os.path.exists(os.path.join(config_dir, 'config.example.json')):
        ex_file = open(os.path.join(config_dir, 'config.example.json'), 'w')
        json.dump({"__Instructions__": "Modify these settings, and save as config.json in " + config_dir
                   , "path":os.path.join(os.path.expanduser('~'),'Dropbox/IFTTT/DropLogger')
                   , "ext": "txt"
                   , "recurse": True
                   , "outputs": ["stdout"]
                   , "output_config" : { "stdout": {"json_output": True}}}, ex_file, indent=4)
        ex_file.close()

    config = {'output_config':{}}
    config['path'] = os.path.join(os.path.expanduser('~'),'Dropbox/IFTTT/DropLogger')
    config['ext'] = 'txt'
    config['recurse'] = True
    config['start'] = datetime.datetime.combine(datetime.date.today(),datetime.time.min.replace(tzinfo=dateutil.tz.tzlocal()))
    config['end']   = config['start'] + datetime.timedelta(days=1)
    config['outputs'] = ["stdout"]

    config['output_config']['stdout'] = {}
    config['output_config']['stdout']['json_output'] = True

    if os.path.exists(config_file):
        try:
            with open(config_file) as f:
                config_file_values = json.load(f)
        except ValueError:
            config_file_values = {}
        def merge_dicts(a, b):
            if not isinstance(b, dict):
                return
            for k, v in b.iteritems():
                if k in a and isinstance(a[k], dict):
                    merge_dicts(a[k], v)
                else:
                    a[k] = v
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
    import importlib,sys,datetime,json

    config = read_config()

    if len(config['outputs']) == 0: sys.exit()
    entries = {}

    files = get_files(config['path'], config['ext'], config['recurse'])
    entries = read_files(config['path'], files, config['ext'], config['start'], config['end'])

    for o in config['outputs']:
        o.add_entries(entries)
