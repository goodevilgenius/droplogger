<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
  <title>{{ title }}</title>
  <link>{{ link }}</link>
  <description>{{ description }}</description>

  {% for entry in entries %}
  <item>
	<title>{{ entry.title }}</title>
	<pubDate>{{ entry.date.strftime('%s')|float|formatdate }}</pubDate>
	{% if entry.url %}<link>{{ entry.url }}</link>{% endif %}
	{% if entry.note %}
	<description>{{ entry.note }}</description>
	{% elif entry.text %}
	<description>{{ entry.text }}</description>
	{% endif %}
  </item>
  {% endfor %}

</rss>
