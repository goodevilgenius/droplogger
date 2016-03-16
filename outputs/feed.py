#!/usr/bin/python

import os, codecs
from email.utils import formatdate

__all__ = ["add_entries"]

config = {"path": os.path.join(os.path.expanduser('~'),'Dropbox','Feed'),
          "author":{"name":"Nobody"},
          "filename":"feed_{1}_{2}_{3}.{0}", "date":"%Y-%m-%d", 
          "date_time":"%c", "formats": ['rss'],
          "ext":{"rss":"xml","atom":"xml","json":"json","jsonp":"js"},
          "jsonp_callback":"drop_feed","stdout":False,
          "feed_link":"https://github.com/goodevilgenius/droplogger/",
          "feed_title":"DropLogger feed for {}"}

def add_entries(entries):
    if not entries: return
    
    if not config["stdout"] and not os.path.isdir(config["path"]): os.makedirs(config["path"])

    import jinja2, json, markdown

    def serialize_json(obj):
        return unicode(obj)

    def json_dumps(obj):
        return json.dumps(obj, default=serialize_json)

    entries_to_send = []
    for log in entries:
        these_entries = {}
        these_entries["entries"] = entries[log]
        these_entries["log"] = log
        these_entries["author"] = config["author"]
        these_entries["title"] = config["feed_title"].format(log)
        use_title = "feed_description" not in config or config["feed_description"] is None
        these_entries["description"] = these_entries["title"] if use_title else config["feed_description"].format(log)
        these_entries["link"] = config["feed_link"]

        entries_to_send.append(these_entries)
        
    templates_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates')
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(templates_path))
    env.filters['formatdate'] = formatdate
    env.filters['json.dumps'] = json_dumps
    env.filters['markdown'] = markdown.markdown

    for form in config['formats']:
        temp = None
        try:
            temp = env.get_template(form + ".tpl")
        except jinja2.exceptions.TemplateNotFound:
            pass
        if temp is None: continue

        for to_send in entries_to_send:
            to_send["config"] = config
            logname = to_send["log"]
            dirname = None
            if logname.count(os.sep) > 0:
                dirname = os.path.dirname(logname)
                tostrip = dirname + os.sep
                logname = logname[len(tostrip):]
            filename = config["filename"].format(config["ext"][form], form, logname, "date")
            f = os.path.join(config["path"], filename) if dirname is None else os.path.join(config["path"], dirname, filename) 
            if dirname is not None:
                if not os.path.isdir(os.path.join(config["path"],dirname)):
                    os.makedirs(os.path.join(config["path"],dirname))
            fo = codecs.open(f, 'w', 'utf-8')
            fo.write(temp.render(to_send))
            fo.close()
            
            
