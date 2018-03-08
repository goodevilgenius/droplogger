#!/usr/bin/python

import os, codecs, datetime
from email.utils import formatdate

__all__ = ["add_entries"]

config = {"path": os.path.join(os.path.expanduser('~'),'Dropbox','Feed'),
          "author":{"name":"Nobody"},
          "filename":"feed_{1}_{2}_{3}.{0}",
          "master_feed":"all_feeds_{1}_{2}.{0}",
          "date":"%Y-%m-%d", 
          "date_time":"%c", "formats": ['rss'],
          "ext":{"rss":"xml","atom":"xml","json":"json","jsonp":"js"},
          "jsonp_callback":"drop_feed",
          "feed_link":"https://github.com/goodevilgenius/droplogger/",
          "feed_title":"DropLogger feed for {}"}

def add_entries(entries):
    if not entries: return
    
    if not os.path.isdir(config["path"]): os.makedirs(config["path"])

    import jinja2, json, markdown
    from xml.sax.saxutils import escape

    def serialize_json(obj):
        return unicode(obj)

    def json_dumps(obj):
        return json.dumps(obj, default=serialize_json)

    entries_to_send = []
    for log in entries:
        these_entries = {}
        these_entries["entries"] = entries[log]
        these_entries["date"] = entries[log][0]['date']
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
    env.filters['escape'] = escape

    for form in config['formats']:
        temp = None
        try:
            temp = env.get_template(form + ".tpl")
        except jinja2.exceptions.TemplateNotFound:
            pass
        if temp is None: continue
        written = []

        for to_send in entries_to_send:
            to_send["config"] = config
            logname = to_send["log"]
            dirname = None
            if logname.count(os.sep) > 0:
                dirname = os.path.dirname(logname)
                tostrip = dirname + os.sep
                logname = logname[len(tostrip):]
            filename = config["filename"].format(config["ext"][form], form, logname, to_send["date"].strftime(config["date"]))
            f = os.path.join(config["path"], filename) if dirname is None else os.path.join(config["path"], dirname, filename) 
            if dirname is not None:
                if not os.path.isdir(os.path.join(config["path"],dirname)):
                    os.makedirs(os.path.join(config["path"],dirname))
            fo = codecs.open(f, 'w', 'utf-8')
            fo.write(temp.render(to_send))
            fo.close()
            written.append((logname,filename if dirname is None else os.path.join(dirname, filename)))

        master_filename = config["master_feed"].format(config["ext"][form], form, to_send["date"].strftime(config["date"]))
        f = os.path.join(config["path"], master_filename)
        master = {"entries":[]}
        master["description"] = config["feed_description"].format(form) if "feed_description" in config else config["feed_title"].format(form)
        master["title"] = config["feed_title"].format(form)
        master["author"] = config["author"]
        master["link"] = config["feed_link"]
        master["date"] = datetime.datetime.now()
        master["config"] = config
        master["log"] = form
        for log in written:
            entry = {}
            entry["title"] = config["feed_title"].format(log[0])
            entry["date"] = datetime.datetime.now()
            entry["author"] = config["author"]
            entry["url"] = log[1]
            master["entries"].append(entry)
        fo = codecs.open(f, 'w', 'utf-8')
        fo.write(temp.render(master))
        fo.close()
