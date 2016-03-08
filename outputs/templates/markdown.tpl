# {{ title }}

{{ diary -}}

{% macro render_log(items, key, depth) -%}
{{ "#"*depth }} {{ key }}

{% if "entries" in items -%}
{% for e in items["entries"] -%}
* {{ e["date"].strftime(config["date_time"]) }} - {% if "url" in e %}[{% endif %}{{ e.title }}{% if "url" in e %}]({{ e.url }}){% endif %}
{% endfor %}
{%- endif %}
{% if "subs" in items -%}
{% for subkey,subitems in items["subs"].iteritems() -%}
{{ render_log(subitems, subkey, depth + 1)}}
{%- endfor %}
{%- endif %}
{%- endmacro %}
{%- for key,items in entries.iteritems() %}
{{- render_log(items, key, 2) -}}
{% endfor -%}