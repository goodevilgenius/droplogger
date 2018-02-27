#!/usr/bin/env python

import os
import os.path
import dateutil
import dateutil.parser as dp
import datetime
import re
import importlib
import json
import sys
from utils.misc import *
from utils.date import *

first_line_re = re.compile("^@begin\s+([^-]+(?:\s-[0-9]{4})?)\s+-\s*(.*)")

def get_files(**kwargs):
    import copy
    
    r = []
    wext = ("." + kwargs['ext']) if (bool)(kwargs['ext']) else ""
    xlen = len(wext)
    has_black = "black" in kwargs and "white" not in kwargs
    has_white = "white" in kwargs
    for f in os.listdir(kwargs['path']):
        full = os.path.join(kwargs['path'], f)
        if kwargs['recurse'] and os.path.isdir(full):
            newkwargs = copy.copy(kwargs)
            newkwargs["path"] = full
            def add_black_white(has, key):
                if has:
                    newl = []
                    for k in kwargs[key]:
                        if k.startswith(f + os.sep):
                            plen = len(f + os.sep)
                            newl.append(k[plen:])
                    newkwargs[key] = newl
            add_black_white(has_black, "black")
            add_black_white(has_white, "white")
            for subf in get_files(**newkwargs):
                r.append(os.path.join(f, subf))
        elif os.path.isfile(full) and f.endswith(wext):
            if has_black and f[:-xlen] in kwargs["black"]: continue
            if has_white and f[:-xlen] not in kwargs["white"]: continue
            r.append(f)
    return r

def parse_item(item):
    yaml_bool = re.compile("^(y|Y|yes|Yes|YES|n|N|no|No|NO|true|True|TRUE|false|False|FALSE|on|On|ON|off|Off|OFF)$")
    yaml_true = re.compile("^(y|Y|yes|Yes|YES|true|True|TRUE|on|On|ON)$")
    yaml_null = re.compile("^(~|null|Null|NULL|none|None|NONE)")

    if is_string(item):
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
        lists = get_config()['lists']
        if lists is None:
            lists = ["tags"]
    if list_separator is None:
        list_separator = get_config()['list_separator']
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
    if not "title" in new or new["title"] is None:
        new["title"] = "Untitled"
    if not is_string(new["title"]):
        new["title"] = get_string(new["title"])
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

def get_config(comargs={}):
    import appdirs

    config_dir = appdirs.user_data_dir('DropLogger','DanielRayJones')
    if not os.path.exists(config_dir): os.makedirs(config_dir)
    config_file = os.path.join(config_dir, 'config.json')

    config = {'output_config':{}}
    config['path'] = os.path.join(os.path.expanduser('~'),'Dropbox','IFTTT','DropLogger')
    config['ext'] = 'txt'
    config['max'] = -1
    config['recurse'] = True
    config['lists'] = ["tags"]
    config['list_separator'] = ","
    config['start'] = parse_date('today')
    config['end']   = parse_date('tomorrow')
    config['outputs'] = ["stdout"]

    config.update(comargs)

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

    get_outputs(config)
    get_all_output_configs(config)

    if not os.path.exists(config_file) and not os.path.exists(os.path.join(config_dir, 'config.example.json')):
        ex_file = open(os.path.join(config_dir, 'config.example.json'), 'w')
        ex_config = {"__Instructions__": "Modify these settings, and save as config.json in " + config_dir
                    , "__lists__": "lists should contain a list of item types to be interpreted as lists"
                    , "path": config['path']
                    , "ext": config['ext']
                    , "recurse": config['recurse']
                    , "lists": config['lists']
                    , "list_separator": config['list_separator']
                    , "outputs": config['original_outputs']
                    , "output_config" : config['original_output_config']
        }
        json.dump(ex_config, ex_file, indent=4)
        ex_file.close()
	
    return config

def get_outputs(config):
    real_outputs = []
    orig_outputs = config['outputs']
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
    config['original_outputs'] = orig_outputs

def get_all_output_configs(config):
    import glob

    configs = {}
    dir_path = os.path.dirname(os.path.realpath(__file__))
    output_path = os.path.join(dir_path, 'outputs')
    files = glob.glob(output_path + os.sep + '*.py')
    for o in files:
        o_mod = os.path.basename(o)[:-3]
        try:
            new_output = importlib.import_module("outputs.%s" % o_mod)
            if "config" in new_output.__dict__ and new_output.config is not None:
                configs[o_mod] = new_output.config
        except ImportError:
            pass

    config['original_output_config'] = configs

def read_command_line():
    import argparse

    config = {"list_logs":False}
    p = argparse.ArgumentParser()
    p.add_argument('--list', '-l', action='store_true', help='Only list the logs')
    p.add_argument('--start', '-s', type=parse_date, help='Start date to parse, use current if omitted')
    p.add_argument('--end'  , '-e', type=parse_date, help='End date to parse, use end of today if omitted')
    p.add_argument('--max', '-m', type=int, help='Max number of items per log')
    p.add_argument('--outputs', '-o', help="Outputs to use")
    p.add_argument('--output_config', '-c', nargs=3, dest='configs', action='append', metavar=('ouptut', 'config','value'), help='Set [output] [config] value as [key]')
    p.add_argument('--white', '-w', action='append', help='Whitelist: only show these logs (use -w multiple times for multiple logs)')
    p.add_argument('--black', '-b', action='append', help="Blacklist: don't show these logs (use -b multiple times for multiple logs) Ignored if any whitelist items are set")
    parsed = p.parse_args()

    config["list_logs"] = parsed.list
    if parsed.start is not None: config["start"] = parsed.start
    if parsed.end is not None: config["end"] = parsed.end
    if parsed.max is not None: config["max"] = parsed.max
    if parsed.outputs is not None: config["outputs"] = re.split(' *, *', parsed.outputs)

    def parse_color(col):
        if getattr(parsed, col) is not None and len(getattr(parsed, col)) > 0:
            config[col] = getattr(parsed, col)
    parse_color("white")
    parse_color("black")

    if parsed.configs is not None:
        config["output_config"] = {}
        for values in parsed.configs:
            if values[0] not in config["output_config"]:
                config["output_config"][values[0]] = {}
            config["output_config"][values[0]][values[1]] = parse_item(values[2])

    return config

if __name__ == "__main__":
    import sys,datetime

    comargs = read_command_line()
    config = get_config(comargs)

    if not config['list_logs']:
        if len(config['outputs']) == 0: sys.exit()

    config['files'] = get_files(**config)
    entries = read_files(**config)

    if config['list_logs']:
        for k in entries.keys():
            print(k)
    else:
        for o in config['outputs']:
            try:
                o.add_entries(entries)
            except:
                sys.stderr.write("An error occurred in %s output\n" % o.__name__.split('.')[-1])
