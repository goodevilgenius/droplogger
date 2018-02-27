#!/usr/bin/env python

import appdirs
import os.path
import importlib
from utils.misc import merge_dicts
from utils.date import parse_date

def get_dir():
    config_dir = appdirs.user_data_dir('DropLogger','DanielRayJones')
    if not os.path.exists(config_dir): os.makedirs(config_dir)

    return config_dir

def get_config_path():
    return os.path.join(get_dir(), 'config.json')

def get_config(comargs={}):
    config_file = get_config_path()

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

    if not os.path.exists(config_file) and not os.path.exists(os.path.join(get_dir(), 'config.example.json')):
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
