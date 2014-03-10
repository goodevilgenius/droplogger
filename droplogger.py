#!/usr/bin/python

import os
import os.path
import dateutil.parser
import datetime
import re

drop_folder = os.path.join(os.path.expanduser('~'),'Dropbox/IFTTT/DropLogger')
file_type = 'txt'
recurse = True
d1 = dateutil.parser.parse('Mar 7 2014')
d2 = dateutil.parser.parse('Mar 8 2014')

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

entries = {}

files = get_files(drop_folder, file_type, recurse)

for f in files:
    these_entries = []
    name = f.rsplit('.'+file_type, 1)[0] if (bool)(file_type) else f
    full = os.path.join(drop_folder, f)
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
                    if date and d1 <= date < d2:
                        these_entries.append(process_entry(entry))
            line = f.readline()
    if len(these_entries) == 0: continue
    if not name in entries:
        entries[name] = these_entries
    else: entries[name].extend(these_entries)

print(entries)
print(len(entries))
