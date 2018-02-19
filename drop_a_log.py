#!/usr/bin/env python

import os, os.path, copy, json
import datetime, dateutil.tz
from droplogger import read_config, merge_dicts, parse_date, is_string

def add_entry(name, entry):
	e = copy.deepcopy(entry)
	c = read_config()
	path = c['path']

	lists = c['lists'] or ["tags"]
	list_separator = c['list_separator'] or ","

	f = name
	if (bool)(c['ext']):
		f += "." + c['ext']

	full_path = os.path.join(path, f)

	if not os.path.isdir(os.path.dirname(full_path)):
		os.makedirs(os.path.dirname(full_path))

	try:
		fp = open(full_path, 'a+')
	except IOError:
		return False

	try:
		fp.seek(-1, os.SEEK_END)
		last = fp.read()
	except IOError:
		last = '\n'
	if last != '\n':
		fp.seek(-1, os.SEEK_END)
		fp.write("\n")

	fp.seek(0,2)
	fp.write("@begin ")
	d = ""
	if not 'date' in e or not e['date']:
		e['date'] = parse_date('now')
	if is_string(e['date']):
		e['date'] = parse_date(e['date'])
	if e['date'].year < 1900:
		d2 = e['date'].replace(year=1900)
		d = d2.strftime('%B %d, %Y at %I:%M:%S%p %z').replace('1900', '%04d' % e['date'].year)
	else: d = e['date'].strftime('%B %d, %Y at %I:%M:%S%p %z')
	fp.write(d)
	del e['date']
	fp.write(' - ')
	fp.write(e['title'])
	del e['title']

	if len(e.keys()) > 0:
		fp.write("\n")

		for k in e:
			t = type(e[k])
			fp.write('@' + k + ' ')
			if t is str or t is unicode:
				fp.write(e[k])
			elif t is int or t is long or t is float:
				fp.write((str)(e[k]))
			elif t is list and k in lists:
				fp.write(list_separator.join(str(x) for x in e[k]))
			else:
				fp.write(json.dumps(e[k]))
			fp.write("\n")

		fp.write("@end\n")
	else:
		fp.write(" @end\n")

	fp.close()

	return True

def parse_drop_args(args):
	name = args.name
	entry = {
		"title": args.title, 
		"date": args.date
		}
	if args.items is not None:
		if 'title' in args.items: del args.items['title']
		if 'date' in args.items: del args.items['date']
		merge_dicts(entry, args.items)
	if args.json is not None:
		if 'title' in args.json: del args.json['title']
		if 'date' in args.json: del args.json['date']
		merge_dicts(entry, args.json)

	if not entry['date']: entry['date'] = datetime.datetime.now(dateutil.tz.tzlocal())

	return name, entry if (bool)(entry['title']) else False

if __name__ == "__main__":
	import argparse, re, json

	class AddItemAction(argparse.Action):
		space_re = re.compile('\s+')

		def __call__(self, parser, namespace, values, option_string=None):
			key = self.space_re.sub('', values[0])
			if key == "": return False
			if not self.dest in namespace or getattr(namespace, self.dest) is None:
				setattr(namespace, self.dest, {})
			getattr(namespace, self.dest)[key] = values[1]

	p = argparse.ArgumentParser()
	p.add_argument("name", help='The name of the log to which this entry will be written')
	p.add_argument("title", help='The title of the entry')
	p.add_argument('--date', '-d', type=parse_date, help='Date of the entry, use current if omitted')
	p.add_argument('--json', '-j', type=json.loads, help='Entire entry (minus title and date) as a JSON object')
	p.add_argument('--item', '-i', nargs=2, dest='items', action=AddItemAction, metavar=('key','value'), help='Add item with [value] as [key]')
	
	name, entry = parse_drop_args(p.parse_args())
	if entry:
		if add_entry(name, entry):
			print("Successfully added entry to %s" % name)
			print("")

			print(entry["title"])
			d = ""
			if entry['date'].year < 1900:
				d2 = entry['date'].replace(year=1900)
				d = d2.strftime('%B %d, %Y at %I:%M:%S%p %z').replace('1900', '%04d' % entry['date'].year)
			else: d = entry['date'].strftime('%B %d, %Y at %I:%M:%S%p %z')
			print(d)
			print("")

			del(entry["title"])
			del(entry["date"])

			for (k,v) in entry.items():
				print("%s: %s" % (k, v if type(v) is str or type(v) is unicode else json.dumps(v)))
		else:
			print("Failed to add entry")
	else:
		print("Failed to parse entry. Please check your input and try again.")
