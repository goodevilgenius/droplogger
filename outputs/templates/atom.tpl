<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>{{ title }}</title>
  <id>tag:droplogger.danielrayjones.com,2015:feed:{{ log }}</id>
  <updated>{{ entries[-1:][0].date.isoformat() }}</updated>
  <author>
	<name>{{ author.name }}</name>
	{%- if author.email %}<email>{{ author.email }}</email>{% endif %}
  </author>

  {% for entry in entries %}
  <entry>
	<title>{{ entry.title }}</title>
	<id>tag:droplogger.danielrayjones.com,2015:feed:{{ log }}:{{ entry.date.strftime('%s') }}</id>
	<updated>{{ entry.date.isoformat() }}</updated>
	{% if entry.url %}<link href="{{ entry.url }}" />{% endif %}
	{% if entry.note -%}
	<summary><![CDATA[{{ entry.note|markdown }}]]></summary>
	{%- elif entry.notes -%}
	<summary><![CDATA[{{ entry.notes|markdown }}]]></summary>
	{%- elif entry.text -%}
	<summary><![CDATA[{{ entry.text|markdown }}]]></summary>
	{%- endif %}
  </entry>
  {% endfor %}
</feed>
