#!/usr/bin/env python
"""Module for adding new droplog entries"""

import os, os.path, copy, json
import datetime, dateutil.tz
from .config import get_config
from .utils.misc import *
from .utils.date import *

def add_entry(name, entry):
	"""Add a new droplog entry to name log

	entry should be a dict having at least a title, and a date
	date should be either a datetime, or a string parseable by utils.date.parse_date
	For all other items, if the value is neither a string or number, it must be passable to json.dumps
	"""
	e = copy.deepcopy(entry)
	c = get_config()
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
		fp.seek(0, os.SEEK_END)
		fp.seek(fp.tell() - 1, os.SEEK_SET)
		last = fp.read()
	except IOError:
		last = '\n'
	if last != '\n':
		fp.seek(0, os.SEEK_END)
		fp.write("\n")

	fp.seek(0,2)
	fp.write("@begin ")

	if not 'date' in e or not e['date']:
		e['date'] = parse_date('now')
	fp.write(format_date(e['date']))
	del e['date']

	fp.write(' - ')
	fp.write(e['title'])
	del e['title']

	if len(e.keys()) > 0:
		fp.write("\n")

		for k in e:
			t = type(e[k])
			fp.write('@' + k + ' ')
			if is_string(e[k]):
				fp.write(e[k])
			elif type(t) is int or type(t) is float:
				fp.write((str)(e[k]))
			elif type(t) is list and k in lists:
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
	"""Helper for parsing command-line arguments, used by main"""
	name = args.name
	entry = {
		"title": args.title, 
		"date": args.date
		}
	def merge_args(arg):
		if arg is not None:
			if 'title' in arg: del arg['title']
			if 'date' in arg: del arg['date']
			merge_dicts(entry, arg)
	merge_args(args.items)
	merge_args(args.json)

	if not entry['date']: entry['date'] = datetime.datetime.now(dateutil.tz.tzlocal())

	return name, entry if (bool)(entry['title']) else False

def main():
	"""entry point for drop-a-log cli command"""
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
			print(format_date(entry['date']))
			print("")

			del(entry["title"])
			del(entry["date"])

			for (k,v) in entry.items():
				print("%s: %s" % (k, v if is_string(v) else json.dumps(v)))
		else:
			print("Failed to add entry")
	else:
		print("Failed to parse entry. Please check your input and try again.")

if __name__ == "__main__":
	main()
