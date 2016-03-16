# {{ title }}

{{ diary -}}

{% macro render_log(items, key, depth) -%}
{{ "#"*depth }} {{ key }}

{% if "entries" in items -%}
{% for e in items["entries"] -%}
* {{ e["date"].strftime(config["date_time"]) }} - {% if "url" in e %}[{% endif %}{{ e.title }}{% if "url" in e %}]({{ e.url }}){% endif %}
{%- if "like" in e %} {% if e.like %}&#x1F44D;{% else %}&#x1F44E;{% endif %}{% endif -%}
{%- if "funny" in e and e["funny"] %} &#x1F606;{% endif -%}
{%- if "boring" in e and e["boring"] %} &#x1F4A4;{% endif -%}
{%- if "rating" in e %} {{ "&#x2B50;"*e.rating }}{% endif -%}
{%- if "notes" in e %}   
  Notes: {{ e.notes -}}
{% elif "note" in e %}   
  Notes: {{ e.note -}}
{%- endif %}
{%- if "tags" in e %}   
  Tags: {{ ", ".join(e.tags) -}}
{%- endif %}
{% endfor %}
{%- endif %}
{% if "subs" in items -%}
{% for subkey,subitems in items["subs"].iteritems() -%}
{{ render_log(subitems, subkey, depth + 1) }}
{%- endfor %}
{%- endif %}
{%- endmacro %}
{%- for key,items in entries.iteritems() %}
{{- render_log(items, key, 2) -}}
{% endfor -%}