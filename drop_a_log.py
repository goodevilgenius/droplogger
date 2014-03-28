#!/usr/bin/python

from droplogger import read_config, merge_dicts

def add_entry(name, entry):
	c = read_config()
	path = c['path']
	print(path)
	print(name)
	print(entry)

	return False

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
	
	return name, entry

if __name__ == "__main__":
	import argparse, re, json
	import dateutil.parser as dp

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
	p.add_argument('--date', '-d', type=dp.parse, help='Date of the entry, use current if omitted')
	p.add_argument('--json', '-j', type=json.loads, help='Entire entry (minus title and date) as a JSON object')
	p.add_argument('--item', '-i', nargs=2, dest='items', action=AddItemAction, metavar=('key','value'), help='Add item with [value] as [key]')
	
	name, entry = parse_drop_args(p.parse_args())
	if entry:
		if add_entry(name, entry):
			print("Successfully added entry")
		else:
			print("Failed to add entry")
	else:
		print("Failed to parse entry. Please check your input and try again.")
