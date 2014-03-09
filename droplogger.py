#!/usr/bin/python

import os
import os.path
import dateutil.parser
import datetime
import re

drop_folder = os.path.join(os.path.expanduser('~'),'Dropbox/IFTTT/DropLogger')
file_type = 'txt'
recurse = True
# without ext = f.rsplit('.'+ext, 1)[0]

def get_files(path, ext, recurse):
    r = []
    for f in os.listdir(path):
        full = os.path.join(path, f)
        if recurse and os.path.isdir(full):
            for subf in get_files(full, ext, True):
                r.append(os.path.join(f, subf))
        elif os.path.isfile(full) and f.endswith('.' + ext):
            r.append(f)
    return r

files = get_files(drop_folder, file_type, recurse)

f = files[0]
d1 = dateutil.parser.parse('Mar 7 2014')
d2 = dateutil.parser.parse('Mar 8 2014')

full = os.path.join(drop_folder, f)
entries = []
first_line_re = re.compile("@begin\s+([^-]+)\s*-\s*(.+)")
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
                    entries.append(entry.strip())
        line = f.readline()

print(entries)
print(len(entries))
