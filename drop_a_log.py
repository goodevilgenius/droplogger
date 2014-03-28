#!/usr/bin/python

from droplogger import read_config

def add_entry(name, entry):
	c = read_config()
	print(c)

def parse_drop_args(args):
	print(args)
	return True

if __name__ == "__main__":
	import argparse

	class AddItemAction(argparse.Action):
		def __call__(self, parser, namespace, values, option_string=None):
			setattr(namespace, values[0], values[1])

	p = argparse.ArgumentParser()
	p.add_argument("name", 'The name of the log to which this entry will be written')
	p.add_argument("title", 'The title of the entry')
	p.add_argument('--date', '-d', help='Date of the entry, use current if omitted')
	p.add_argument('--json', '-j', help='Entire entry (minus title and date) as a JSON object')
	p.add_argument('--item', '-i', nargs=2, action=AddItemAction, metavar=('key','value'), help='Add item with [value] as [key]')
	
	name, entry = parse_drop_args(p.parse_args())
	if entry:
		if add_entry(name, entry):
			print("Successfully added entry")
		else:
			print("Failed to add entry")
	else:
		print("Failed to parse entry. Please check your input and try again.")
