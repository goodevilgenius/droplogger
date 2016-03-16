<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
  <title>{{ title }}</title>
  <link>{{ link }}</link>
  <description>{{ description }}</description>

  {% for entry in entries %}
  <item>
	<guid isPermaLink="false">tag:droplogger.danielrayjones.com,2015:feed:{{ log }}:{{ entry.date.strftime('%s') }}</guid>
	<title>{{ entry.title|escape }}</title>
	<pubDate>{{ entry.date.strftime('%s')|float|formatdate }}</pubDate>
	{% if entry.url %}<link>{{ entry.url }}</link>{% endif %}
	{% if entry.note %}
	<description><![CDATA[{{ entry.note|markdown }}]]></description>
	{% elif entry.notes %}
	<description><![CDATA[{{ entry.notes|markdown }}]]></description>
	{% elif entry.text %}
	<description><![CDATA[{{ entry.text|markdown }}]]></description>
	{% endif %}
  </item>
  {% endfor %}
</channel>
</rss>
