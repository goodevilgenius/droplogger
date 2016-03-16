# DropLogger

DropLogger is a program that takes logs of your activities, and creates journal
files (and many other things) from those logs.

It's designed to be used with IFTTT and Dropbox, but is flexible enough to be
used in a variety of different ways. You're only limited by your imagination.

## Log files

All the log files reside in the same directory (by default
~/Dropbox/IFTTT/DropLogger) and have a very specific format. It's a plain text
file, but each log entry is formatted like this:

    @begin <entry-date-and-time> - <title>
	@key value
	@key2 this entry is long, and spans
	multiple lines
	@number 4
	@bool True
	@end

Each text file is named for the particular log. For example, you might log all
the places you've been in a file called places.txt, and an entry might look like
this: 

    @begin March 5, 2015 at 12:15PM - White House
	@url http://4sq.com/316GgA
	@end

You could also include other information, such as latitude and longitude, in
each log. To generate this log, you could use the IFTTT Foursquare Recipe in the
IFTTT Samples section below.

The only parts of the log entry that are required are `@begin` at the beginning,
`@end` at the end, and the date and the title. So, if you wanted to keep a log
of short notes, you could create a file called notes.txt that looked like this:

    @begin February 3, 2015 at 01:33PM - Remember to call Mom @end
	@begin February 4, 2015 at 07:45AM - Breakfast today was great! @end

## Output

Just having a bunch of log files by themselves isn't that interesting. You want
to do something with this. That's what this program is all about. The program
allows you to use any number of outputs to change these logs into a format
that's more useful to you. When the program is run, it takes all the log entries
from the previous day, and sends them to the pre-selected outputs. The program
currently comes with three outputs: `stdout`, `feed`, `markdown_journal`, and
`mongo`.

### stdout

The first output is `stdout`. All this does is print the log entries to the
console in an easy-to-read format. It can also output them in JSON format. This
output was mostly made for testing purposes, but it could also be redirected to
a file and used however you see fit.

Its config is simple:

    {"json_output": false, "indent": true}

### feed

This output can generate an `RSS`, `ATOM`, or `JSON` feed for each log. These
can be exported to a website in any way you see fit, or used for any other
purpose.

This might be especially useful run regularly with specific command-line
arguments. E.g., I like to do something like this:

    droplogger -o feed -s min -e now -m 5 -w tracks -w watched

That command generates feeds of the five latest entries for my tracks and
watched logs. `-s min` guarantees that it will grab as far back as it needs to
to find the last five. This is useful if a log doesn't have any entries for the
past day.

Here are the configuration options:

```json
{"path": "~/Dropbox/Feed", "author":
 {"name":"Nobody","email":"my.email@example.com"}
 "filename":"feed_{1}_{2}_{3}.{0}", "date":"%Y-%m-%d", "date_time":"%c",
 "formats": ['rss'],
 "ext":{"rss":"xml","atom":"xml","json":"json","jsonp":"js"},
 "jsonp_callback":"drop_feed",
 "feed_link":"https://github.com/goodevilgenius/droplogger/",
 "feed_title":"DropLogger feed for {}"}
```

The `author` will be used in the `<author>` field in the `ATOM`
feed. `author.email` is optional.

The `filename` will substite the extenstion for `{0}`, the `format` for `{1}`,
the log name for `{2}`, and the `date` for `{3}`. Feel free to leave any of
those out.

`formats` should be an array of any of the following: `rss`, `atom`, `json`,
and/or `jsonp`.

`ext` defines the file extension for each format.

`jsonp_callback` defines the callback function for the `JSONP` feed.

`feed_link` will change the main feed link. It defaults to droplogger's GitHub
page, but you may change it to your own website, if you wish.

`feed_title` will be the title of the feed. `{}` will be the name of the log
(i.e., the filename).

### Markdown Journal

The second output is `markdown_journal`. This creates a single file each day
intended to be used as a daily journal. The file is in [Markdown][md] format,
which is, in itself, fairly easy to read, but can also be converted to HTML to
be viewed in a web browser (with an external tool).

Each file is named Journal_YYYY-MM-DD.md, where YYYY-MM-DD is the current
date. Each log has a separate section, with a list of each log entry. If a `url`
is included with the entry, the title is a link to it. Other items in the log
are ignored.

It also looks for a log called `diary` and treats those entries specially. Each
`diary` entry for that day should have a `text` item. That text is output
directly as is at the top of the journal.

[md]: http://daringfireball.net/projects/markdown/syntax

#### mongodb

The final output is to send each entry to a mongo database. 

## Config file

**TODO**

## Command-line arguments

Droplogger supports a few command-line arguments that override values specified
in the config file. The following are supported:

* --list, -l: List the logs, without actually processing the entries. It only
	prints logs that have entries within the specified time period. So, to find
	logs from all time, do the following: `droplogger -l -s min -e now`
* --start, -s: This defines the start time to parse. Normally, this is the
	beginning of the current day.
* --end, -e: This defines the end time to parse. Normally this is right now.
* --max, -m: This is the maximum number of items for each log. Defaults to all
* --outputs, -o: Which outputs to use
* --output_config, -c: configure outputs. E.g., `droplogger -o stdout -c stdout json_output true`
	uses stdout, with json output, regardless of what's set in the config file

## IFTTT Samples

* [IFTTT Recipe: Add Fourquare checkins to #DropLogger](https://ifttt.com/view_embed_recipe/267058-add-checkins-to-droplogger)
* [IFTTT Recipe: Add completed tasks to #DropLogger](https://ifttt.com/recipes/397512-add-completed-tasks-to-droplogger)
* [IFTTT Recipe: Add my tweets to #DropLogger](https://ifttt.com/recipes/397513-add-my-tweets-to-droplogger)
* [IFTTT Recipe: Write in my #DropLogger #diary](https://ifttt.com/recipes/397514-write-in-my-droplogger-diary)

**More to come**

## Future enhancements

* Finish this documentation
* Provide API documentation
