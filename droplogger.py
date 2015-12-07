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

def get_files(**kwargs):
    r = []
    wext = ("." + kwargs['ext']) if (bool)(kwargs['ext']) else ""
    for f in os.listdir(kwargs['path']):
        full = os.path.join(kwargs['path'], f)
        if kwargs['recurse'] and os.path.isdir(full):
            for subf in get_files(path=full, ext=kwargs['ext'], recurse=True):
                r.append(os.path.join(f, subf))
        elif os.path.isfile(full) and f.endswith(wext):
            r.append(f)
    return r

def parse_item(item):
    yaml_bool = re.compile("^(y|Y|yes|Yes|YES|n|N|no|No|NO|true|True|TRUE|false|False|FALSE|on|On|ON|off|Off|OFF)$")
    yaml_true = re.compile("^(y|Y|yes|Yes|YES|true|True|TRUE|on|On|ON)$")
    yaml_null = re.compile("^(~|null|Null|NULL|none|None|NONE)")

    if isinstance(item, str):
        # Let's figure out what type this is

        # First let's make sure it's not empty
        item = item.strip()
        if not (bool)(item):
            return None
        if yaml_null.match(item):
            return None

        # Check for a YAML (or JSON) boolean value
        if yaml_bool.match(item):
            item = bool(yaml_true.match(item))
            return item

        # Next see if it's an int
        try:
            val = int(item)
            return val
        except ValueError:
            pass

        # Or a flot
        try:
            val = float(item)
            return val
        except ValueError:
            pass

        # Or a date
        try:
            val = dp.parse(item)
            return val
        except (TypeError, ValueError):
            pass

        # Finally check if it's valid json
        try:
            val = json.loads(item)
            return val
        except ValueError:
            pass

        # If none of these passed, it's still a string
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
            if k == "json":
                try:
                    newitems = json.loads(new[k])
                    if "date" in newitems: del newitems["date"]
                    if "title" in newitems: del newitems["title"]
                    
                    for jsonk in newitems.keys():
                        newk = parse_item(newitems[jsonk])
                        if newk is not None:
                            new[jsonk] = newk

                    del new["json"]
                    continue
                except ValueError:
                    pass
            newk = parse_item(new[k])
            if newk is not None:
                new[k] = newk
            else:
                del new[k]
    return new

def read_files(**kwargs):
    import codecs
    
    entries = {}
    for f in kwargs['files']:
        these_entries = []
        name = f.rsplit('.'+kwargs['ext'], 1)[0] if (bool)(kwargs['ext']) else f
        full = os.path.join(kwargs['path'], f)
        with codecs.open(full, encoding='utf-8') as f:
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
                        if date and kwargs['start'] <= date < kwargs['end']:
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
        if kwargs['max'] > 0:
            entries[k] = entries[k][-kwargs['max']:]

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
    config['max'] = -1
    config['recurse'] = True
    config['lists'] = ["tags"]
    config['list_separator'] = ","
    # config['start'] = datetime.datetime.combine(datetime.date.today() - datetime.timedelta(days=1),datetime.time.min.replace(tzinfo=dateutil.tz.tzlocal()))
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
	
    return config

def get_outputs(config):
    real_outputs = []
    for o in config['outputs']:
        try:
            new_output = importlib.import_module("outputs.%s" % o)
            if o in config['output_config']:
                for k in config['output_config'][o]:
                    new_output.config[k] = config['output_config'][o][k]
            real_outputs.append(new_output)
        except ImportError:
            pass
    config['outputs'] = real_outputs

def read_command_line():
    import argparse

    def parse_date(date):
        r = None
        switch = {
            "min": datetime.datetime.min,
            "max": datetime.datetime.max,
            "now": datetime.datetime.now(),
            "today": datetime.datetime.combine(datetime.date.today(),datetime.time.min.replace(tzinfo=dateutil.tz.tzlocal())),
            }
        oneday = datetime.timedelta(days=1)
        switch["tomorrow"] = switch["today"] + oneday
        switch["yesterday"] = switch["today"] - oneday

        if date.lower() in switch: r = switch[date.lower()]
        else:
            r = dp.parse(date)
            
        if r.tzinfo is None:
            r = r.replace(tzinfo = dateutil.tz.tzlocal())
        return r

    config = {}
    p = argparse.ArgumentParser()
    p.add_argument('--start', '-s', type=parse_date, help='Start date to parse, use current if omitted')
    p.add_argument('--end'  , '-e', type=parse_date, help='End date to parse, use end of today if omitted')
    p.add_argument('--max', '-m', type=int, help='Max number of items per log')
    p.add_argument('--outputs', '-o', help="Outputs to use")
    p.add_argument('--output_config', '-c', nargs=3, dest='configs', action='append', metavar=('ouptut', 'config','value'), help='Set [output] [config] value as [key]')
    parsed = p.parse_args()

    if parsed.start is not None: config["start"] = parsed.start
    if parsed.end is not None: config["end"] = parsed.end
    if parsed.max is not None: config["max"] = parsed.max
    if parsed.outputs is not None: config["outputs"] = re.split(' *, *', parsed.outputs)
    if parsed.configs is not None:
        config["output_config"] = {}
        for values in parsed.configs:
            if values[0] not in config["output_config"]:
                config["output_config"][values[0]] = {}
            config["output_config"][values[0]][values[1]] = parse_item(values[2])

    return config

if __name__ == "__main__":
    import sys,datetime

    config = read_config()
    comargs = read_command_line()
    config.update(comargs)
    get_outputs(config)

    if len(config['outputs']) == 0: sys.exit()

    config['files'] = get_files(**config)
    entries = read_files(**config)

    for o in config['outputs']:
        o.add_entries(entries)
