#!/usr/bin/python

import os
import os.path
import dateutil.parser
import datetime
import re

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
    first_line_re = re.compile("^@begin\s+([^-]+)\s*-\s*(.+)")
    other_lines_re = re.compile("^@([^\s]+)\s*(.*)")
    
    lines = entry.splitlines()
    m = first_line_re.match(lines.pop(0))
    if not m: return False
    try:
        new["date"] = dateutil.parser.parse(m.groups()[0])
    except:
        return False
    k = "title"
    new[k] = m.groups()[1].strip().rsplit('@end',1)[0].strip()
    newline = lines.pop(0)
    while newline:
        m = other_lines_re.match(newline)
        while not m:
            new[k] += "\n" + newline.strip().rsplit('@end',1)[0].strip()
            newline = lines.pop(0)
        k = m.groups()[0]
        if k == "end": break
        new[k] = m.groups()[1].strip().rsplit('@end',1)[0].strip()
        try:
            newline = lines.pop(0)
        except:
            newline = False
    for k in new.keys():
        if not (bool)(new[k]): del new[k]
    return new

first_line_re = re.compile("^@begin\s+([^-]+)\s*-\s*(.+)")

if __name__ == "__main__":
    import importlib,sys

    config = {'output_config':{}}
    config['input'] = os.path.join(os.path.expanduser('~'),'Dropbox/IFTTT/DropLogger')
    config['ext'] = 'txt'
    config['recurse'] = True
    config['start'] = dateutil.parser.parse('Mar 7 2014')
    config['end']   = dateutil.parser.parse('Mar 8 2014')
    config['outputs'] = ["stdout"]

    config['output_config']['stdout'] = {}
    config['output_config']['stdout']['json_output'] = True

    real_outputs = []
    for o in config['outputs']:
        try:
            real_outputs.append(importlib.import_module("outputs.%s" % o))
            if o in config['output_config']:
                for k in config['output_config'][o]:
                    real_outputs[len(real_outputs)-1].config[k] = config['output_config'][o][k]
        except:
            True

    if len(real_outputs) == 0: sys.exit()
    entries = {}

    files = get_files(config['input'], config['ext'], config['recurse'])

    for f in files:
        these_entries = []
        name = f.rsplit('.'+config['ext'], 1)[0] if (bool)(config['ext']) else f
        full = os.path.join(config['input'], f)
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
                            date = dateutil.parser.parse(date)
                        except:
                            date = False
                        if date and config['start'] <= date < config['end']:
                            these_entries.append(process_entry(entry))
                line = f.readline()
        if len(these_entries) == 0: continue
        if not name in entries:
            entries[name] = these_entries
        else: entries[name].extend(these_entries)

    for o in real_outputs:
        o.add_entries(entries)
