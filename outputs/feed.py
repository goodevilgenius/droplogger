#!/usr/bin/python

import os

__all__ = ["add_entries"]

config = {"path": os.path.join(os.path.expanduser('~'),'Dropbox','Feed'),
          "filename":"feed_{1}_{2}.{0}", "date":"%Y-%m-%d", 
          "date_time":"%c", "formats": ['rss'],
          "ext":{"rss":"xml","atom":"xml","json":"json","jsonp":"js"},
          "jsonp_callback":"drop_feed","stdout":False,
          "feed_link":"https://github.com/goodevilgenius/droplogger/",
          "feed_title":"DropLogger feed for {}"}

def add_entries(entries):
    if not entries: return
    print(config) # DEBUG
    
    if not config["stdout"] and not os.path.isdir(config["path"]): os.mkdir(config["path"])

    import jinja2

    entries_to_send = []
    for log in entries:
        these_entries = {}
        these_entries["entries"] = entries[log]
        these_entries["log"] = log
        these_entries["title"] = config["feed_title"].format(log)
        use_title = "feed_description" not in config or config["feed_description"] is None
        these_entries["description"] = these_entries["title"] if use_title else config["feed_description"].format(log)
        these_entries["link"] = config["feed_link"]

        entries_to_send.append(these_entries)
        
        
    
    templates_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates')
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(templates_path))

    for form in config['formats']:
        temp = None
        try:
            temp = env.get_template(form + ".tpl")
        except jinja2.exceptions.TemplateNotFound:
            pass

        if temp is None: continue
        for to_send in entries_to_send:
            print(to_send)
            print(temp.render(to_send))
            
            
