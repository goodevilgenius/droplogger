#!/usr/bin/python

import os

__all__ = ["add_entries"]

config = {"path": os.path.join(os.path.expanduser('~'),'Dropbox','Feed'),
          "filename":"feed_{1}_{2}.{0}", "date":"%Y-%m-%d", 
          "date_time":"%c", "formats": ['rss'],
          "ext":{"rss":"xml","atom":"xml","json":"json","jsonp":"js"},
          "jsonp_callback":"drop_feed","stdout":False}

def add_entries(entries):
    if not entries: return
    print(config) # DEBUG
    
    if not config["stdout"] and not os.path.isdir(config["path"]): os.mkdir(config["path"])

    import jinja2
    
    templates_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates')
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(templates_path))

    for form in config['formats']:
        temp = None
        try:
            temp = env.get_template(form + ".tpl")
        except jinja2.exceptions.TemplateNotFound:
            pass

        if temp is None: continue
        for log in entries:
            print(log)
            the_entries = entries[log]
            print(temp.render({"entries":the_entries,"log": log}))
            
            
