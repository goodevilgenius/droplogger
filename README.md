# DropLogger

DropLogger is the Dropbox (+IFTTT) logger. It is a program that takes logs of your activities, and creates journal files (and many other things) from those logs.

It's designed to be used with IFTTT and Dropbox, but is flexible enough to be used in a variety of different ways. You're only limited by your imagination.

## Log files

All the log files reside in the same directory (by default `~/Dropbox/IFTTT/DropLogger`) and have a very specific format. It's a plain text file, wherein each log entry is formatted like this:

```
@begin <entry-date-and-time> - <title>
@key value
@key2 this entry is long, and spans
multiple lines
@number 4
@bool True
@end
```

When `droplogger` processes this entry, it generates an object similar to the following JSON:

```json
{
  "title": "<title>",
  "date": "2016-01-01T12:13:14Z",
  "key": "value",
  "key2": "this entry is long, and spans\nmultiple lines",
  "number": 4,
  "bool": true
}
```

Each text file is named for the particular log. For example, you might log all the places you've been in a file called places.txt, and an entry might look like this:

```
@begin March 5, 2015 at 12:15PM - White House
@url http://4sq.com/316GgA
@end
```

You could also include other information, such as latitude and longitude, in each log. To generate this log, you could use the IFTTT Foursquare Recipe in the IFTTT Samples section below.

The only parts of the log entry that are required are `@begin` at the beginning, `@end` at the end, and the date and the title. So, if you wanted to keep a log of short notes, you could create a file called notes.txt that looked like this:

```
@begin February 3, 2015 at 01:33PM - Remember to call Mom @end
@begin February 4, 2015 at 07:45AM - Breakfast today was great! @end
```

## Output

Just having a bunch of log files by themselves isn't that interesting. You want to do something with this. That's what this program is all about. The program allows you to use any number of outputs to change these logs into a format that's more useful to you. When the program is run, it takes all the log entries from the previous day, and sends them to the pre-selected outputs. The program currently comes with four outputs: `stdout`, `feed`, `markdown_journal`, and `mongo`.

### stdout

The first output is `stdout`. All this does is print the log entries to the console in an easy-to-read format. It can also output them in JSON format. This output was mostly made for testing purposes, but it could also be redirected to a file and used however you see fit.

Its config is simple:

```json
{"json_output": false, "indent": true}
```

### feed

This output can generate an `RSS`, `ATOM`, or `JSON` feed for each log. These can be exported to a website in any way you see fit, or used for any other purpose.

This might be especially useful run regularly with specific command-line arguments. E.g., I like to do something like this:

```shell
droplogger -o feed -s min -e now -m 5 -w tracks -w watched
```

That command generates feeds of the five latest entries for my tracks and watched logs. `-s min` guarantees that it will grab as far back as it needs to to find the last five. This is useful if a log doesn't have any entries for the past day.

Here are the configuration options:

```json
{"path": "~/Dropbox/Feed",
 "author": {"name":"Nobody","email":"my.email@example.com"},
 "filename":"feed_{1}_{2}_{3}.{0}",
 "master_feed":"all_feeds_{1}_{2}.{0}",
 "date":"%Y-%m-%d", "date_time":"%c",
 "formats": ["rss"],
 "ext":{"rss":"xml","atom":"xml","json":"json","jsonp":"js"},
 "jsonp_callback":"drop_feed",
 "feed_link":"https://github.com/goodevilgenius/droplogger/",
 "feed_title":"DropLogger feed for {}"}
```

The `author` will be used in the `<author>` field in the `ATOM` feed. `author.email` is optional.

The `filename` will substite the extenstion for `{0}`, the `format` for `{1}`, the log name for `{2}`, and the `date` for `{3}`. Feel free to leave any of those out.

The `master_feed` will include a list of all the available feeds. The extension will be `{0}`; the `format` will be `{1}` and the `date` will be `{2}`.

`formats` should be an array of any of the following: `rss`, `atom`, `json`, and/or `jsonp`.

`ext` defines the file extension for each format.

`jsonp_callback` defines the callback function for the `JSONP` feed.

`feed_link` will change the main feed link. It defaults to droplogger's GitHub page, but you may change it to your own website, if you wish.

`feed_title` will be the title of the feed. `{}` will be the name of the log (i.e., the filename).

### Markdown Journal

The next output is `markdown_journal`. This creates a single file each day intended to be used as a daily journal. The file is in [Markdown][md] format, which is, in itself, fairly easy to read, but can also be converted to HTML to be viewed in a web browser (with an external tool).

Each file is named Journal_YYYY-MM-DD.md, where YYYY-MM-DD is the current date. Each log has a separate section, with a list of each log entry. If a `url` is included with the entry, the title is a link to it. Other items in the log are ignored.

It also looks for a log called `diary` and treats those entries specially. Each `diary` entry for that day should have a `text` item. That text is output directly as is at the top of the journal.

[md]: http://daringfireball.net/projects/markdown/syntax

#### mongodb

The final output is to send each entry to a mongo database. Types of each value are retained, including the date.

## Config file

The configuration file will be found in a system-specific location. Here are a few places it might be:

* On macOS: ~/Library/Preferences/DropLogger
* On Windows XP: C:\Documents and Settings\<username>\Application Data\DanielRayJones\DropLogger
* On Windows 7: C:\Users\<username>\AppData\Local\DanielRayJones\DropLogger
* On RedHat-based Linuxes: ~/.local/share/DropLogger
* On other Unix and Unix-like systems: ~/.config/DropLogger

There will be an example config file there, called `config.example.json`. It should be renamed to `config.json` and modified according to your intended usage.

When you first launch `droplogger`, you will see the following message:

```
No config file present. Using default values.
Please move /path/to/config.example.json to /path/to/config.json, and set values as appropriate
```

In this way, you can discover the exact location of your config file.

The file must be valid JSON. There are instructions within the file itself as to what values may be used.

## Command-line arguments

Droplogger supports a few command-line arguments that override values specified in the config file. The following are supported:

* `--list`, `-l`: List the logs, without actually processing the entries. It only
	prints logs that have entries within the specified time period. So, to find
	logs from all time, do the following: `droplogger -l -s min -e now`
* `--start`, `-s`: This defines the start time to parse. Normally, this is the
	beginning of the current day.
* `--end`, `-e`: This defines the end time to parse. Normally this is right now.
* `--max`, `-m`: This is the maximum number of items for each log. Defaults to all
* `--outputs`, `-o`: Which outputs to use
* `--output_config`, `-c`: configure outputs. E.g., `droplogger -o stdout -c stdout json_output true`
	uses stdout, with json output, regardless of what's set in the config file
* `--white`, `-w`: whitelist the log. Only process that log. May be used multiple times.
* `--black`, `-b`: blacklist the log. Processes all but that log. May be used multiple times.
* `--help`, `-h`: Print help and quit

## IFTTT Samples

* [IFTTT Recipe: Add Fourquare checkins to #DropLogger](https://ifttt.com/view_embed_recipe/267058-add-checkins-to-droplogger)
* [IFTTT Recipe: Add completed tasks to #DropLogger](https://ifttt.com/recipes/397512-add-completed-tasks-to-droplogger)
* [IFTTT Recipe: Add my tweets to #DropLogger](https://ifttt.com/recipes/397513-add-my-tweets-to-droplogger)
* [IFTTT Recipe: Write in my #DropLogger #diary](https://ifttt.com/recipes/397514-write-in-my-droplogger-diary)

**More to come**

## Adding entries from the command line

`droplogger` comes with a command-line script called `drop-a-log` which can be used to add new entries (without having to go through IFTTT).

It's usage is very simple, and invoking `drop-a-log --help` should tell you all you need to know, but here are a few examples of usage.

`drop-a-log notes "I am so tired right now"` adds to the `notes` log:

```
@begin February 15, 2018 at 06:51:39PM +0000 - I am so tired right now @end
```

```shell
drop-a-log tracks -d 1999-05-04T06:30 "(You Drive Me) Crazy by Britney Spears" \
   -i url https://www.last.fm/music/Britney+Spears/_/(You+Drive+Me)+Crazy
   -i artist "Britney Spears"
   -i album "...Baby One More Time"
   -i song "(You Drive Me) Crazy"
```

The format for the date after `-d` is very flexible. Try out a few things and see what works. This command adds the following to the `tracks` log.

```
@begin May 4, 1999 at 06:30:00PM +0000 - (You Drive Me) Crazy by Britney Spears
@url https://www.last.fm/music/Britney+Spears/_/(You+Drive+Me)+Crazy
@artist Britney Spears
@album ...Baby One More Time
@song (You Drive Me) Crazy
@end
```

`drop-a-log data "Arbitrary Data" -j '{"field1":"a string","field2":42,"field3":true}'` adds to the `data` log:

```
@begin February 15, 2018 at 06:51:39PM +0000 - Arbitrary Data
@field1 a string
@field2 42
@field3 true
@end
```

The `-j` option lets you send your entire entry as a JSON-encoded string.

## Using as a Python module

The application includes an easy-to-use module for adding other droplog entries. The following example should get you started:

```python
from droplogger.drop_a_log import add_entry
from datetime import datetime

entry = {"title": "A new entry"}
entry['date'] = datetime.now()
entry['rating'] = 5
entry['like'] = True

add_entry('logname', etnry)
```

This will add the following entry to `logname.txt`:

```
@begin February 15, 2018 at 06:51:39PM +0000 - A new entry
@rating 5
@like true
@end
```

The `date` may be ommitted, in which case, the current time will be used. The `date` may also be a string which is parseable by `dateutil.parser`.
