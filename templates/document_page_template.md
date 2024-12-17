type:: Document
key:: {{ document.key }}

{% for annotation in annotations %}
{% if annotation.type == "note" %}
- 🖊️ {{ annotation.text }}
mtime:: {{ annotation.mtime }}
{% else %}
- 📖 {{ annotation.text }}
mtime:: {{ annotation.mtime }}
{% endif %}
{% endfor %}
